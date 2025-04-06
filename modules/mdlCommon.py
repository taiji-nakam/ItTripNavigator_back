# 共通モジュール
import json
from db_control import crud, mymodels
from fastapi.responses import JSONResponse
from fastapi import HTTPException

# 全ての選択情報を取得
def getAllIssues() -> tuple[int, str]:
    """
    m_industry, m_company_size, m_department, m_theme の4つのテーブルデータをまとめて取得する。
    - 全て 200 の場合: 4つのデータをまとめた JSON を返す (status=200)
    - いずれかが 404 の場合: 全体を 404 として扱い、その 404 メッセージを返す
    - その他のステータス(例: 500など)があれば、その時点で HTTPException を発生させる
    """
    # 各種データを取得
    status_i, result_i = getIndustry()
    status_c, result_c = getCompanySize()
    status_d, result_d = getDepartment()
    status_t, result_t = getTheme()

    # ステータスコードをまとめてチェック
    #    - いずれかが 404 なら全体を 404 にする
    #    - その他のステータス(200, 404以外)があれば例外を投げる
    for (status, result) in [
        (status_i, result_i),
        (status_c, result_c),
        (status_d, result_d),
        (status_t, result_t)
    ]:
        if status == 404:
            # どれか1つでも 404 があれば全体を 404 として返す
            return 404, result
        elif status != 200:
            # 404 以外で 200 でなければ例外発生
            raise HTTPException(
                status_code=status,
                detail=json.loads(result)
            )

    # ここまで来たら全て 200
    #    各 result は JSON文字列 なので、Pythonオブジェクトに変換してまとめる
    data = {
        "industry": json.loads(result_i),
        "company_size": json.loads(result_c),
        "department": json.loads(result_d),
        "theme": json.loads(result_t)
    }

    # 結果を JSON文字列 にして返す
    return 200, json.dumps(data, ensure_ascii=False)

# 業界情報を取得
def getIndustry() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_industry()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No m_industry data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# 企業規模情報を取得
def getCompanySize() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_company_size()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No m_company_size data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# 部署情報を取得
def getDepartment() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_department()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No m_department data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# テーマ情報を取得
def getTheme() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_theme()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No m_theme data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

# 職種情報を取得
def getJob() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_job()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No m_job data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す