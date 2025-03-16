# 共通モジュール
import json
from db_control import crud, mymodels
from fastapi.responses import JSONResponse
from fastapi import HTTPException

# 全ての選択情報を取得
def getIndustry() -> tuple[int, str]:
    # 業界情報の取得
    status, result = crud.select_m_industry()

    # 結果が `None` の場合、デフォルト値を設定
    if result is None:
        result = json.dumps({"message": "No data available"}, ensure_ascii=False)

    # ステータスコードに応じた処理
    if status == 404:
        return status, result  # そのまま返す
    elif status != 200:
        raise HTTPException(
            status_code=status,
            detail=json.loads(result)
        )
    return status, result  # 正常時もTuple[int, str] を返す

