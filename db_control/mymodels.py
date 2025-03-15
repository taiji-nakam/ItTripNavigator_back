from sqlalchemy import ForeignKey,DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

# 支援領域: talent_supportarea
class talent_supportarea(Base):
    __tablename__ = "talent_supportarea"
    supportarea_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(primary_key=True)
    supportarea_title: Mapped[str] = mapped_column()
    supportarea_detail: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()

# マインドセット: talent_mindset
class talent_mindset(Base):
    __tablename__ = "talent_mindset"
    mindset_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(primary_key=True)
    mindset_description: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()

# 経歴: talent_career
class talent_career(Base):
    __tablename__ = "talent_career"
    career_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(primary_key=True)
    career_description: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()

# 人材_ハッシュタグ対照表: talent_hashtag
class talent_hashtag(Base):
    __tablename__ = "talent_hashtag"
    talent_id: Mapped[int] = mapped_column(primary_key=True)
    hashtag_id: Mapped[int] = mapped_column(primary_key=True)

# ハッシュタグマスタ: m_hashtag
class m_hashtag(Base):
    __tablename__ = "m_hashtag"
    hashtag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hashtag_name: Mapped[str] = mapped_column()

# 検索履歴(詳細): d_search
class d_search(Base):
    __tablename__ = "d_search"
    search_id: Mapped[int] = mapped_column(primary_key=True)
    search_id_sub: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(nullable=True)
    job_id: Mapped[int] = mapped_column(nullable=True)
    search_ymd: Mapped[datetime] = mapped_column()

# 事例_業界対照表: case_industry
class case_industry(Base):
    __tablename__ = "case_industry"
    case_id: Mapped[int] = mapped_column(primary_key=True)
    industry_id: Mapped[int] = mapped_column(primary_key=True)

# 事例_企業規模対照表: case_company_size
class case_company_size(Base):
    __tablename__ = "case_company_size"
    company_size_id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(primary_key=True)

# 事例_部署対照表: case_department
class case_department(Base):
    __tablename__ = "case_department"
    case_id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(primary_key=True)

# 事例_テーマ対照表: case_theme
class case_theme(Base):
    __tablename__ = "case_theme"
    case_id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(primary_key=True)

# 事例: m_case
class m_case(Base):
    __tablename__ = "m_case"
    case_id: Mapped[int] = mapped_column(primary_key=True)
    case_name: Mapped[str] = mapped_column()
    case_summary: Mapped[str] = mapped_column()
    company_summary: Mapped[str] = mapped_column()
    initiative_summary: Mapped[str] = mapped_column()
    issue_background: Mapped[str] = mapped_column()
    solution_method: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column(default=True)

# テーマ: m_theme
class m_theme(Base):
    __tablename__ = "m_theme"
    theme_id: Mapped[int] = mapped_column(primary_key=True)
    theme_name: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column(default=True)

# 部署: m_department
class m_department(Base):
    __tablename__ = "m_department"
    department_id: Mapped[int] = mapped_column(primary_key=True)
    department_name: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column(default=True)

# 企業規模: m_company_size
class m_company_size(Base):
    __tablename__ = "m_company_size"
    company_size_id: Mapped[int] = mapped_column(primary_key=True)
    company_size_name: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column(default=True)

# 業界: m_industry
class m_industry(Base):
    __tablename__ = "m_industry"
    industry_id: Mapped[int] = mapped_column(primary_key=True)
    industry_name: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column(default=True)


# 以下参考
# class m_product(Base):
#     __tablename__ = 'm_product_taig'
#     prd_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     code:Mapped[str] = mapped_column()
#     name:Mapped[str] = mapped_column()
#     price:Mapped[int] = mapped_column()
#     from_date:Mapped[datetime] = mapped_column()
#     to_date:Mapped[datetime] = mapped_column()

# class m_tax(Base):
#     __tablename__ = 'm_tax_taig'
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     code: Mapped[str] = mapped_column(unique=True)
#     name: Mapped[str] = mapped_column()
#     percent: Mapped[float] = mapped_column()

# class t_transaction(Base):
#     __tablename__ = 't_transaction_taig'
#     trd_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     datetime: Mapped[str] = mapped_column()
#     emp_cd: Mapped[str] = mapped_column()
#     store_cd: Mapped[str] = mapped_column()
#     pos_no: Mapped[str] = mapped_column()
#     total_amt: Mapped[int] = mapped_column()
#     ttl_amt_ex_tax: Mapped[int] = mapped_column()

# class d_transaction_details(Base):
#     __tablename__ = 'd_transaction_details_taig'
#     trd_id: Mapped[int] = mapped_column(ForeignKey('t_transaction_taig.trd_id'), primary_key=True)  # 取引 ID（FK）
#     dtl_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 明細 ID（PK）
#     prd_id: Mapped[int] = mapped_column(ForeignKey('m_product_taig.prd_id'))  # 商品 ID（FK）
#     prd_code: Mapped[str] = mapped_column()
#     prd_name: Mapped[str] = mapped_column()
#     prd_price: Mapped[int] = mapped_column()
#     tax_cd: Mapped[str] = mapped_column(ForeignKey('m_tax_taig.code'))  # 税コード（FK）

# class m_promotion_plan(Base):
#     __tablename__ = 'm_promotion_plan_taig'
#     prm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # プロモーションID（PK）
#     prm_code: Mapped[str] = mapped_column()  # プロモーションコード（13桁）
#     from_date: Mapped[datetime] = mapped_column()  # 開始日（デフォルト現在時刻）
#     to_date: Mapped[datetime] = mapped_column()  # 終了日（NULL 許可）
#     name: Mapped[str] = mapped_column()  # プロモーション名（最大50文字）
#     percent: Mapped[float] = mapped_column()  # 割引率（5桁、少数2桁）
#     discount: Mapped[int] = mapped_column()  # 割引額（整数）
#     prd_id: Mapped[int] = mapped_column(ForeignKey('m_product_taig.prd_id'), nullable=False)  # 商品 ID（FK）

# # 以下 削除予定
# class assessment_answer(Base):
#     __tablename__ = 'assessment_answer'
#     assessment_id:Mapped[int] = mapped_column(ForeignKey("assessment.assessment_id"), primary_key=True)
#     question_id:Mapped[int] = mapped_column(primary_key=True)
#     answer:Mapped[int] = mapped_column()

# class assessment_result(Base):
#     __tablename__ = 'assessment_result'
#     assessment_id:Mapped[int] = mapped_column(ForeignKey("assessment.assessment_id"), primary_key=True)
#     category:Mapped[str] = mapped_column(primary_key=True)
#     priority:Mapped[int] = mapped_column()

# class basic_info(Base):
#     __tablename__ = 'basic_info'
#     assessment_id:Mapped[int] = mapped_column(ForeignKey("assessment.assessment_id"), primary_key=True)
#     age_group:Mapped[str] = mapped_column()
#     country_origin:Mapped[str] = mapped_column()
#     nearest_station:Mapped[str] = mapped_column()
#     time_tostation:Mapped[int] = mapped_column()
#     budget_lower_limit:Mapped[int] = mapped_column()
#     budget_upper_limit:Mapped[int] = mapped_column()
#     area_fg_smaller:Mapped[int] = mapped_column()
#     area_fg_average:Mapped[int] = mapped_column()
#     area_fg_larger:Mapped[int] = mapped_column()
#     # MySQL変更時に沼りそうなのでboolは使わずint(0:no,1:yes)で実装始める

# class area_result(Base):
#     __tablename__ = 'area_result'
#     assessment_id:Mapped[int] = mapped_column(ForeignKey("assessment.assessment_id"), primary_key=True)
#     recommended:Mapped[str] = mapped_column()
#     note:Mapped[str] = mapped_column()
#     latitude: Mapped[float] = mapped_column(DECIMAL(9, 6))  # 緯度
#     longitude: Mapped[float] = mapped_column(DECIMAL(9, 6))  # 経度

# # # TEST Table
# class Customers(Base):
#     __tablename__ = 'customers'
#     customer_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     customer_name:Mapped[str] = mapped_column()
#     age:Mapped[int] = mapped_column()
#     gender:Mapped[str] = mapped_column()
    