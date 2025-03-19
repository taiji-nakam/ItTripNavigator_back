from pydantic import BaseModel
from typing import List,Optional

class searchIdData(BaseModel):
    search_id: Optional[int] = None # 検索ID
    search_id_sub: Optional[int] = None #検索サブID

# 事例検索履歴登録のデータモデル
class caseSearchData(BaseModel):
    search_id: Optional[int] = None # 検索ID
    search_id_sub: Optional[int] = None #検索サブID
    industry_id: int  # 業界ID
    company_size_id: int  # 企業規模ID
    department_id: int  # 部署ID
    theme_id: int # テーマID
    