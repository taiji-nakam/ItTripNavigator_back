
import json
from db_control import crud
from fastapi import HTTPException
import vectorstore_global
from models.params import talentSearchData
from typing import Final

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
   
    # TODO 
    # 人材検索→職種取得、事例検索→事例取得
    # それぞれのケースでプロンプト作成
    # 結果の成形 ※OpenAI使う？

    # 職種情報の取得
    status, result = crud.select_m_job_from_search(search_id, search_id_sub)
    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message:No m_job data available"}, ensure_ascii=False)
    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )

    # 取得した職種情報から job_name を取り出し、プロンプトを作成する
    try:
        job_data = json.loads(result)
        job_name = job_data.get("job_name", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing job information: " + str(e))
    prompt = f"職種: {job_name}。 {job_name}に優れた人材を抽出してください。名前、エグゼクティブサマリー、経歴は必ず加えてください。"
    #ex) ERP導入に向いている人を抽出してください。名前、エグゼクティブサマリー、経歴は必ず加えてください。

    if vectorstore_global.talent_vectorstore is None:
        raise HTTPException(status_code=500, detail="Vectorstore is not initialized.")

    # FAISSのretrieverを作成し、上位3件の関連ドキュメントを検索する例
    retriever = vectorstore_global.talent_vectorstore.as_retriever(search_kwargs={"k": 4})
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
    
    return status, result_texts  # 正常時はTuple[int, str] を返す


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
