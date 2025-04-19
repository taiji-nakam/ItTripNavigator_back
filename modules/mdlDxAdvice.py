import json
import re
from db_control import crud
from fastapi import HTTPException
from models.params import caseSearchData, dxAdviceData
from typing import Final,Dict
import vectorstore_global
# from dotenv import load_dotenv
import os
import openai

SEARCH_MODE: Final[int] = 2  #アドバイス取得のため2を指定

def build_chatgpt_advice_and_rag_prompt(data: dxAdviceData) -> str:
    timing = data.timing or "不明なタイミング"
    domain = data.domain or "不明な課題"
    has_free = bool(data.free_word)
    free_text = data.free_word.strip() if has_free else ""

    prompt = f"""
あなたはDXに精通した熟練のITコンサルタントです。
クライアントから以下の情報が提供されています：

- 現在のフェーズ（タイミング）：{timing}
- 解決したい課題領域：{domain}"""

    if has_free:
        prompt += f"\n- 現場の背景・具体的な悩み：{free_text}"

    prompt += """

この情報をもとに、以下の2つの出力をしてください：

① <<START_ADVICE>> 〜 <<END_ADVICE>> で囲まれた領域に、400字程度のDX推進に向けたアドバイスを書いてください。
- フェーズに応じた最初の取り組み方針を提案してください。
- 課題領域に関して、熟練の視点で助言を与えてください。
- 現場の悩みがある場合は、それにも配慮してください（任意）。
- 最後に、関連する代表的なDX事例を1文で紹介してください。

② <<START_PROMPT>> 〜 <<END_PROMPT>> で囲まれた領域に、
ベクトル検索（RAG）用のシンプルな検索用プロンプトを日本語で作成してください。
- 内容はできる限り簡潔にし、「探したい事例の特徴・目的・課題」を箇条書き風または短文で表現してください。
- ChatGPTのような複雑な理解はできない前提で、単純なキーワード検索でも意味が通じるように意識してください。

出力形式の例は以下のとおりです：

<<START_ADVICE>>
（400字のアドバイス）
<<END_ADVICE>>

<<START_PROMPT>>
・中期計画策定フェーズの事例  
・業務効率化が目的  
・受発注業務の属人化を解消した取り組み
<<END_PROMPT>>
""".strip()

    return prompt

# アドバイスを生成し参考事例を取得する
def getAdviceCase(data:dxAdviceData) -> tuple[int, str]:
    
    ############################################################
    # 1.検索データをDBへ登録
    ############################################################
    status, new_search_id = crud.insert_search(SEARCH_MODE)  
    if status != 200 or new_search_id is None:
        # insert_searchに失敗した場合はそのまま返す
        return status, "Search creation failed"
    # d_search作成用のcaseDataを生成
    caseData = caseSearchData(
        search_id=new_search_id,
        search_id_sub=None,
        industry_id=None,
        company_size_id=None,
        department_id=None,
        theme_id=None,
        case_id=None,
    )

    # d_search 新規作成し検索サブIDを取得
    status, result = crud.insert_d_search_case(caseData)

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
    new_search_sub_id = int(result)

    ############################################################
    # 2.現状を踏まえたアドバイスを作成 
    ############################################################
    # prompt作成
    prompt = build_chatgpt_advice_and_rag_prompt(data)
    print(prompt)
    advice = "アドバイス(Sample)"
    prompt_rag = "いい感じの事例を抽出してください"
    DO_GPT = os.getenv("DO_GPT") 
    if DO_GPT == "TRUE":
        # GPTによる戦略文書生成
        openai.api_key = os.getenv("OPEN_AI_API_KEY")
        response =  openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt},],
        )
        # レスポンスを解析
        output_content = response.choices[0].message.content.strip()
        # デバッグ用: GPTの出力を確認
        print("GPT Raw Output:", output_content)

        # アドバイス部分を抽出
        start_marker = "<<START_ADVICE>>"
        end_marker = "<<END_ADVICE>>"
        start_index = output_content.find(start_marker)
        end_index = output_content.find(end_marker)
        if start_index != -1 and end_index != -1:
            # マーカー直後から開始、終了マーカー直前までを抽出
            advice = output_content[start_index + len(start_marker):end_index].strip()

        # プロンプト部分を抽出
        start_marker = "<<START_PROMPT>>"
        end_marker = "<<END_PROMPT>>"
        start_index = output_content.find(start_marker)
        end_index = output_content.find(end_marker)
        if start_index != -1 and end_index != -1:
            # マーカー直後から開始、終了マーカー直前までを抽出
            prompt_rag = output_content[start_index + len(start_marker):end_index].strip()

    print(advice)
    print(prompt_rag)

    ############################################################
    # 3.参考事例を抽出 
    ############################################################
    # ベクトルストアが初期化されていない場合のエラーハンドリング
    if vectorstore_global.case_vectorstore is None:
        raise HTTPException(status_code=500, detail="Case vectorstore is not initialized.")

    # FAISSのretrieverを作成（上位4件を取得）
    retriever = vectorstore_global.case_vectorstore.as_retriever(search_kwargs={"k": 4})
    results = retriever.get_relevant_documents(prompt)

    print(prompt)
    print("----- Retrieved Case Documents -----")
    parsed_results = []
    for i, doc in enumerate(results):
        candidate_text = f"----- Candidate {i+1} -----\n" + doc.page_content
        print(candidate_text)
        parsed = parse_case_result(candidate_text)
        parsed_results.append(parsed)
    print("----- End of Case Documents -----")

    # id, title, summary のみを抽出
    compact_cases = []
    for case in parsed_results:
        compact_case = {
            "id": case.get("id", ""),
            "title": case.get("title", ""),
            "summary": case.get("summary", "")
        }
        compact_cases.append(compact_case)

    # 正常時(200) → data.search_id と 新規発行された search_id_sub を返す
    new_search_sub_id = int(result)
    final_json = json.dumps(
        {
            "search_id": new_search_id,
            "search_id_sub": new_search_sub_id,
            "advice": advice,
            "prompt": prompt_rag,
            "cases": compact_cases  # ← 修正済み（3項目のみ）
        },
        ensure_ascii=False
    )
    return status, final_json

def parse_case_result(candidate_text: str) -> Dict[str, str]:
    """
    事例データ用：candidate_text から各セクションを抽出し辞書に変換。
    キーワードと対応キー：
      「【ID】」             -> id
      「【事例名】」         -> title
      「【事例概要】」       -> summary
    """
    # ヘッダー（"----- Candidate X -----"）を削除
    candidate_text = re.sub(r"^----- Candidate \d+ -----\n", "", candidate_text)

    # 正規表現で「【◯◯】」に続く内容を抽出
    matches = re.findall(r"【(.*?)】\s*([\s\S]*?)(?=【|$)", candidate_text)

    mapping = {
        "ID": "id",
        "事例名": "title",
        "事例概要": "summary",
    }

    sections = {}
    for key, value in matches:
        std_key = mapping.get(key.strip(), key.strip())
        sections[std_key] = value.strip()

    return sections
