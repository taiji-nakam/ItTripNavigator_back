
import json
from db_control import crud
from fastapi import HTTPException
import vectorstore_global

# 人材情報を取得
def getTalent(search_id, search_id_sub) -> tuple[int, str]:
   
    # 職種情報の取得
    status, result = crud.select_m_job(search_id, search_id_sub)
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
    prompt = f"職種: {job_name} で有能な人を抽出してください"

    if vectorstore_global.talent_vectorstore is None:
        raise HTTPException(status_code=500, detail="Vectorstore is not initialized.")

    # FAISSのretrieverを作成し、上位3件の関連ドキュメントを検索する例
    retriever = vectorstore_global.talent_vectorstore.as_retriever(search_kwargs={"k": 1})
    results = retriever.get_relevant_documents(prompt)

    # 検索結果の各ドキュメント内容を標準出力に出力
    print(prompt)
    print("----- Retrieved Documents -----")
    for doc in results:
        print(doc.page_content)
    print("----- End of Documents -----")

    return status, result  # 正常時もTuple[int, str] を返す