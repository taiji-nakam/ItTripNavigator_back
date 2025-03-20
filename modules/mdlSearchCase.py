# 事例検索処理モジュール
import json
from db_control import crud, mymodels
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from models.params import caseSearchData,setCaseData
from typing import Final
# from dotenv import load_dotenv
import os

SEARCH_MODE: Final[int] = 0  #事例検索のため0を指定

# 検索情報を生成する
def createSearchCase(data:caseSearchData) -> tuple[int, str]:
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

# 事例リストを取得
def getCaseList(search_id, search_id_sub) -> tuple[int, str]:

    # 事例リストの取得
    status, result = crud.select_m_case_list(search_id, search_id_sub)

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": f"No m_case data available for search_id: {search_id}, search_id_sub: {search_id_sub}"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# 代表的な事例リストを取得
def getFeaturedCaseList() -> tuple[int, str]:

    # 取得数
    # load_dotenv()
    FEATURED_COUNT = int(os.getenv("FEATURED_COUNT"))

    # 代表事例リストの取得
    status, result = crud.select_featured_m_case_list(FEATURED_COUNT)

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message:No featured m_case data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す


# 選択された事例を登録
def updateSearchCase(data:setCaseData) -> tuple[int, str]:

    # 選択された事例を検索履歴(詳細)へ登録
    status, result = crud.update_d_search_case(data.search_id, data.search_id_sub, data.case_id)

    # Status異常時の処理
    if status == 404:
        # エラーメッセージをJSON形式にして返す
        return status, json.dumps({"message": result}, ensure_ascii=False)
    elif status != 200:
        # resultがNoneの場合、空の辞書を代わりに使用
        error_detail = json.loads(result) if result is not None else {"error": "Unknown error"}
        raise HTTPException(
            status_code=status,
            detail=error_detail
        )
    else: 
        # 正常時(200) → data.search_id と 新規発行された search_id_sub を返す
        # (既に事例IDが登録されている場合は新しく検索サブIDを発行しFrontへ戻す)
        new_search_sub_id = int(result)
        final_json = json.dumps(
            {
                "search_id": data.search_id,
                "search_id_sub": new_search_sub_id
            },
            ensure_ascii=False
        )
        result = final_json

    return status, result

# 事例詳細を取得
def getCaseDetail(search_id, search_id_sub) -> tuple[int, str]:

    # 事例リストの取得
    status, result = crud.select_m_case(search_id, search_id_sub)

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": f"No m_case_detal data available for search_id: {search_id}, search_id_sub: {search_id_sub}"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す
