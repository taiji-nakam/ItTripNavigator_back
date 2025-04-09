
import json
import re
from db_control import crud
from fastapi import HTTPException
import vectorstore_global
from models.params import talentSearchData
from typing import Final, Dict

# 人材情報に対してプロンプトを実行し結果を返す
def getTalentByPrompt(prompt,cnt) -> tuple[int, str]:

    status = 200

    if vectorstore_global.talent_vectorstore is None:
        raise HTTPException(status_code=500, detail="Vectorstore is not initialized.")

    # FAISSのretrieverを作成し、上位3件の関連ドキュメントを検索する例
    retriever = vectorstore_global.talent_vectorstore.as_retriever(search_kwargs={"k": cnt})
    results = retriever.get_relevant_documents(prompt)

    # 検索結果の各ドキュメント内容を標準出力に出力
    print(prompt)
    print("----- Retrieved Documents -----")
    result_texts = []
    for i, doc in enumerate(results):
        candidate_text = f"----- Candidate {i+1} -----\n" + doc.page_content
        print(candidate_text)
        result_texts.append(candidate_text)
    print("----- End of Documents -----")

    return status, result_texts


# 人材情報を取得
def getTalent(search_id, search_id_sub) -> tuple[int, str]:
   
    # 事例または職種情報の取得
    status, result = crud.check_case_or_job(search_id, search_id_sub)
    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )

    # 取得した結果（JSON文字列）をパースする
    try:
        result_data = json.loads(result)
        flag = result_data.get("flag")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing response: " + str(e))
    
    prompt_base = "に優れた人材を抽出してください。名前、エグゼクティブサマリー、経歴は必ず加えてください。"
    # flag の値に応じてプロンプトを作成
    if flag == 0:
        # flag==0 の場合、m_case から取得した情報なので case_name が存在するはず
        case_name = result_data.get("case_name", "")
        prompt = f"事例: {case_name}の推進{prompt_base}"
    elif flag == 1:
        # flag==1 の場合、m_job から取得した情報なので job_name が存在するはず
        job_name = result_data.get("job_name", "")
        prompt = f"職種: {job_name}。 {job_name}{prompt_base}"
        #ex) ERP導入に向いている人を抽出してください。名前、エグゼクティブサマリー、経歴は必ず加えてください。
    else:
        # 万が一 flag の値が期待外れの場合は 500 エラー
        raise HTTPException(status_code=500, detail="Unexpected flag value in response")  
    
    if vectorstore_global.talent_vectorstore is None:
        raise HTTPException(status_code=500, detail="Vectorstore is not initialized.")

    # FAISSのretrieverを作成し、上位3件の関連ドキュメントを検索する例
    retriever = vectorstore_global.talent_vectorstore.as_retriever(search_kwargs={"k": 4})
    results = retriever.get_relevant_documents(prompt)

    # 検索結果の各ドキュメント内容を標準出力に出力
    print(prompt)
    print("----- Retrieved Documents -----")
    parsed_results = []
    for i, doc in enumerate(results):
        # 各候補のテキストを組み立て（ヘッダーも含む）
        candidate_text = f"----- Candidate {i+1} -----\n" + doc.page_content
        print(candidate_text)
        parsed_candidate = parse_candidate(candidate_text)
        parsed_results.append(parsed_candidate)
    print("----- End of Documents -----")
    
    # result_texts はリストになっているので、JSON文字列に変換して返す
    return status, json.dumps(parsed_results, ensure_ascii=False)

def parse_candidate(candidate_text: str) -> Dict[str, str]:
    """
    candidate_text から各セクションを抽出して辞書に変換する。
    キーワードと対応するキーは以下の通り：
      「【名前】」                -> name
      「【エグゼクティブサマリー】」 -> summary
      「【業界情報】」            -> industry
      「【経歴】」                -> career
      「【マインドセット】」      -> mindset
      「【支援領域】」            -> supportarea
      「【保有職種】」            -> job
      「【ハッシュタグ】」        -> hashtag
    """
    # 候補のヘッダー部分（"----- Candidate X -----"）を削除
    candidate_text = re.sub(r"^----- Candidate \d+ -----\n", "", candidate_text)
    
    # 正規表現で「【◯◯】」に続く内容を抽出
    # (?=【|$) で次の【が出るまでまたはテキストの終わりまでを対象にします
    matches = re.findall(r"【(.*?)】\s*([\s\S]*?)(?=【|$)", candidate_text)
    
    mapping = {
        "名前": "name",
        "エグゼクティブサマリー": "summary",
        "業界情報": "industry",
        "経歴": "career",
        "マインドセット": "mindset",
        "支援領域": "supportarea",
        "保有職種": "job",
        "ハッシュタグ": "hashtag"
    }
    
    sections = {}
    for key, value in matches:
        std_key = mapping.get(key.strip(), key.strip())
        sections[std_key] = value.strip()
    return sections
    
SEARCH_MODE: Final[int] = 1  #人員検索のため1を指定

# 検索情報を生成する
def createSearchTalent(data:talentSearchData) -> tuple[int, str]:
    # search_idが空（None、またはFalseな値）の場合にt_search新規作成
    if not data.search_id:
        status, new_search_id = crud.insert_search(SEARCH_MODE)  
        if status != 200 or new_search_id is None:
            # insert_searchに失敗した場合はそのまま返す
            return status, "Search creation failed"
        # 新しく取得した search_id を data にセット
        data.search_id = new_search_id

    # d_search 新規作成し検索サブIDを取得
    status, result = crud.insert_d_search(data)

    # Status異常時の処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        # resultがNoneの場合、空の辞書を代わりに使用
        error_detail = json.loads(result) if result is not None else {"error": "Unknown error"}
        raise HTTPException(
            status_code=status,
            detail=error_detail
        )

    # 正常時(200) → data.search_id と 新規発行された search_id_sub を返す
    #    insert_d_search の戻り値 result は "search_id_sub" を文字列化したものを想定
    new_search_sub_id = int(result)
    final_json = json.dumps(
        {
            "search_id": data.search_id,
            "search_id_sub": new_search_sub_id
        },
        ensure_ascii=False
    )
    return status, final_json
