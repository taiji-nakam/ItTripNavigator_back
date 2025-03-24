from pydantic import BaseModel
from typing import List,Optional

class searchIdData(BaseModel):
    search_id: Optional[int] = None # 検索ID
    search_id_sub: Optional[int] = None # 検索サブID

# 事例検索履歴登録のデータモデル
class caseSearchData(BaseModel):
    search_id: Optional[int] = None # 検索ID
    search_id_sub: Optional[int] = None # 検索サブID
    industry_id: Optional[int] = None   # 業界ID
    company_size_id: Optional[int] = None   # 企業規模ID
    department_id: Optional[int] = None   # 部署ID
    theme_id: Optional[int] = None  # テーマID

# 事例履歴(事例ID)登録のデータモデル
class setCaseData(BaseModel):
    search_id: int # 検索ID
    search_id_sub: int # 検索サブID
    case_id : int # 事例ID

# ユーザ情報登録のデータモデル
class userEntryData(BaseModel):
    search_id: int # 検索ID
    search_id_sub: int # 検索サブID
    mail_address: Optional[str] = None # メールアドレス
    phone_no: Optional[str] = None # 電話番号
    company_name: Optional[str] = None # 会社名
    deparment_name: Optional[str] = None # 部署
    job_title: Optional[str] = None # 役職
    user_name: Optional[str] = None # 名前

class userData(BaseModel):
    search_id: int # 検索ID
    search_id_sub: int # 検索サブID
    user_id: Optional[str] = None # ユーザーID

