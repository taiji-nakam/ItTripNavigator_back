# ユーザ向けアクションモジュール
import json
from models.params import  userData, strategyData
from db_control import crud
from fastapi import HTTPException
import os
import openai

def create_strategy_prompt(user: dict, detail: dict, case: dict) -> str:
    """
    受け取った user, detail, case の情報をもとに、ChatGPT に戦略文書をMarkdown形式で作成してもらうための
    プロンプト文を生成します。ITリテラシーが低い人でも分かりやすい表現を心掛けてください。
    
    ※ 以下の点に留意してください：
      - 3. 必要な資源（人材、技術、設備など）の「ソフトウェアライセンス」では、Salesforce、HubSpot、Microsoft Dynamics 365 など
        の具体例を示すとともに、企業規模に応じた調達費用の目安も記載してください。
      - 4. 簡易なコスト見積もりでは、各項目ごとに「〇〇円～〇〇円」という形で、企業規模に応じた具体的な金額幅を示してください。
      - 5. タイムラインの概要は、各フェーズのおおよその期間（例：要件定義フェーズ：1〜3ヶ月、設計・開発フェーズ：4〜9ヶ月、テストフェーズ：10〜12ヶ月、本番運用フェーズ：13ヶ月以降）を示し、各フェーズで実施するタスクの概要も記載してください。
    
    戻り値は、改行を "\\n" に置換した1行の文字列です。
    """
    # 各情報を取得（存在しなければ空文字）
    industry = detail.get("industry_name", "")
    company_size = detail.get("company_size_name", "")
    department = detail.get("department_name", "")
    theme = detail.get("theme_name", "")
    
    case_name = case.get("case_name", "")
    case_summary = case.get("case_summary", "")
    
    prompt = (
        "あなたは熟練のITコンサルタントです。以下の情報をもとに、分かりやすい表現でMarkdown形式の戦略文書を作成してください。余計なコメントは含めず、"
        "戦略文書部分のみを出力してください。\\n\\n"
        "【業界】：" + industry + "\\n"
        "【企業規模】：" + company_size + "\\n"
        "【部署】：" + department + "\\n"
        "【テーマ】：" + theme + "\\n\\n"
        "【指定事例】\\n"
        "事例名：" + case_name + "\\n"
        "事例概要：" + case_summary + "\\n\\n"
        "【戦略文書の章立て】\\n"
        "1. プロジェクトの概要\\n"
        "   - プロジェクト名\\n"
        "   - 目的と目標\\n"
        "   - 背景と必要性\\n"
        "2. ビジネスインパクト\\n"
        "   - 期待されるビジネス効果\\n"
        "   - 現在の課題とその解決策\\n"
        "3. 主要なステークホルダーとリソース計画\\n"
        "   - 関係者リスト\\n"
        "   - 必要な資源（人材、技術、設備など）：特に、ソフトウェアライセンス（例：Salesforce、HubSpot、Microsoft Dynamics 365 など）を挙げ、"
        "指定した【企業規模】に応じた調達費用の目安も示してください。指定した【企業規模】以外の例示は必要はありません。\\n"
        "   - リソースの配分と管理\\n"
        "4. 簡易なコスト見積もり\\n"
        "   - 初期投資の概算：例えば、企業規模が『〜50億円』の場合は3億円～5億円、企業規模が『50億円〜100億円』の場合は5億円～8億円、などの目安を示してください。\\n"
        "   - ハードウェア・インフラ費用：例）1億円～2億円\\n"
        "   - 人件費：例）5000万円～1億円\\n"
        "   - その他の費用：例）5000万円～1億円\\n"
        "5. タイムラインの概要\\n"
        "   - 主要なマイルストーンと予定スケジュール：例えば、要件定義フェーズは1〜3ヶ月、設計・開発フェーズは4〜9ヶ月、テストフェーズは10〜12ヶ月、本番運用フェーズは13ヶ月以降とし、各フェーズでのタスク概要も記載してください。\\n\\n"
        "必ず戦略文書部分を以下のマーカーで囲んで出力してください。\\n"
        "<<START_STRATEGY>>\\n"
        "<<END_STRATEGY>>"
    )
    
    return prompt

# 戦略文書を作成する
def createDoc(data: userData) -> tuple[int, str]:
    # ユーザー情報を取得
    status, user_json = crud.select_m_user(data.user_id)
    if status == 404:
        return status, json.dumps({"message": "User not found"}, ensure_ascii=False)
    elif status != 200:
        error_detail = json.loads(user_json) if user_json is not None else {"get user error": "Unknown error"}
        raise HTTPException(status_code=status, detail=error_detail)
    
    # ユーザー情報はJSON文字列なので、必要に応じてパース（ここではプロンプト作成に利用するかもしれません）
    user_dict = json.loads(user_json)
    
    # 検索情報を取得
    status, detail_json = crud.select_d_search(data.search_id, data.search_id_sub)
    if status == 404:
        return status, json.dumps({"message": "d_search record not found"}, ensure_ascii=False)
    elif status != 200:
        error_detail = json.loads(detail_json) if detail_json is not None else {"get d_search error": "Unknown error"}
        raise HTTPException(status_code=status, detail=error_detail)
    # ここで detail_json を辞書型に変換
    detail_dict = json.loads(detail_json)
    
    # 元となる事例情報を取得
    status, case_json = crud.select_m_case(data.search_id, data.search_id_sub)
    if status == 404:
        return status, json.dumps({"message": "Case data not found"}, ensure_ascii=False)
    elif status != 200:
        error_detail = json.loads(case_json) if case_json is not None else {"get case error": "Unknown error"}
        raise HTTPException(status_code=status, detail=error_detail)
    # 事例情報も辞書型に変換（必要なら）
    case_dict = json.loads(case_json)
    
    # 戦略文書作成のプロンプトを生成する。引数は全て辞書型にする
    prompt = create_strategy_prompt(user_dict, detail_dict, case_dict)
    strategy_doc = prompt
   
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
        # 戦略文書部分を抽出
        start_marker = "<<START_STRATEGY>>"
        end_marker = "<<END_STRATEGY>>"
        start_index = output_content.find(start_marker)
        end_index = output_content.find(end_marker)
        if start_index != -1 and end_index != -1:
            # マーカー直後から開始、終了マーカー直前までを抽出
            strategy_doc = output_content[start_index + len(start_marker):end_index].strip()
        else:
            # マーカーが見つからなければ、全体を戦略文書とする（またはエラー処理）
            strategy_doc = output_content
    else:
        # GPTトークン節約
        strategy_doc = os.getenv("SAMPLE_DOC") 

    # 戦略文書を登録
    status, result = crud.insert_t_document(data.search_id, data.search_id_sub, strategy_doc)
    if status == 404:
        return status, json.dumps({"message": result}, ensure_ascii=False)
    elif status != 200:
        error_detail = json.loads(result) if result is not None else {"error": "Unknown error"}
        raise HTTPException(status_code=status, detail=error_detail)
    
    return status, result

# 戦略文書を取得
def getDoc(search_id, search_id_sub, document_id) -> tuple[int, str]:

    # 指定されたsearch_id, search_id_sub, document_idの組み合わせを確認
    status,result = crud.check_t_document(search_id, search_id_sub, document_id)
    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    
    # 戦略文書の取得
    status, result = crud.select_t_document(document_id)

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message:No featured t_document data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# 戦略文書ダウンロードを登録
def updateDocDl(data: strategyData) -> tuple[int, str]:
# 戦略文書データを更新
    status, result = crud.update_t_document(data.document_id)
    if status == 404:
        return status, json.dumps({"message": result}, ensure_ascii=False)
    elif status != 200:
        error_detail = json.loads(result) if result is not None else {"error": "Unknown error"}
        raise HTTPException(status_code=status, detail=error_detail)
    
    return status, result
