from sqlalchemy import ForeignKey,DECIMAL, Nullable
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import List

class Base(DeclarativeBase):
    pass

# 職種: m_job
class m_job(Base):
    __tablename__ = "m_job"

    job_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("m_role.role_id"))
    job_name: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column()
     # talent_job 経由で紐づくタレントたち
    talents: Mapped[List["talent_job"]] = relationship("talent_job", back_populates="job")

# 人材職種対照表: talent_job
class talent_job(Base):
    __tablename__ = "talent_job"

    talent_id: Mapped[int] = mapped_column(ForeignKey("m_talent.talent_id"), primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("m_job.job_id"), primary_key=True)

    talent: Mapped["m_talent"] = relationship("m_talent", back_populates="jobs")
    job: Mapped["m_job"] = relationship("m_job", back_populates="talents")

# 人材: m_talent
class m_talent(Base):
    __tablename__ = "m_talent"
    
    talent_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    summary: Mapped[str] = mapped_column()
    industry: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    is_visible: Mapped[bool] = mapped_column()
    
    # リレーション: 子テーブルを取得するため
    careers: Mapped[List["talent_career"]] = relationship("talent_career", back_populates="talent")
    mindsets: Mapped[List["talent_mindset"]] = relationship("talent_mindset", back_populates="talent")
    supportareas: Mapped[List["talent_supportarea"]] = relationship("talent_supportarea", back_populates="talent")
    jobs: Mapped[List["talent_job"]] = relationship("talent_job", back_populates="talent")

# 支援領域: talent_supportarea
class talent_supportarea(Base):
    __tablename__ = "talent_supportarea"
    supportarea_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(ForeignKey("m_talent.talent_id"))
    supportarea_title: Mapped[str] = mapped_column()
    supportarea_detail: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    talent = relationship("m_talent", back_populates="supportareas")

# マインドセット: talent_mindset
class talent_mindset(Base):
    __tablename__ = "talent_mindset"
    mindset_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(ForeignKey("m_talent.talent_id"))
    mindset_description: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    talent = relationship("m_talent", back_populates="mindsets")

# 経歴: talent_career
class talent_career(Base):
    __tablename__ = "talent_career"
    career_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    talent_id: Mapped[int] = mapped_column(ForeignKey("m_talent.talent_id"))
    career_description: Mapped[str] = mapped_column()
    display_order: Mapped[int] = mapped_column()
    talent = relationship("m_talent", back_populates="careers")

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

# 検索履歴: d_search
class t_search(Base):
    __tablename__ = "t_search"
    search_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column()
    search_ymd: Mapped[datetime] = mapped_column(nullable=False)
    search_mode: Mapped[int] = mapped_column(nullable=False)  #0:事例検索,1:人員検索

# 検索履歴(詳細): d_search
class d_search(Base):
    __tablename__ = "d_search"
    search_id: Mapped[int] = mapped_column(primary_key=True)
    search_id_sub: Mapped[int] = mapped_column(primary_key=True)
    industry_id: Mapped[int] = mapped_column()
    company_size_id: Mapped[int] = mapped_column()
    department_id: Mapped[int] = mapped_column()
    theme_id: Mapped[int] = mapped_column()
    case_id: Mapped[int] = mapped_column()
    job_id: Mapped[int] = mapped_column()
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

class m_user(Base):
    __tablename__ = "m_user"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    mail_address: Mapped[str] = mapped_column()
    phone_no: Mapped[str] = mapped_column()
    company_name: Mapped[str] = mapped_column()
    department_name: Mapped[str] = mapped_column()
    job_title: Mapped[str] = mapped_column()
    user_name: Mapped[str] = mapped_column()
    entry_ymd: Mapped[datetime] = mapped_column()

class c_user_id(Base):
    __tablename__ = "c_user_id"
    increment_no: Mapped[int] = mapped_column(primary_key=True)

class t_document(Base):
    __tablename__ = "t_document"
    document_id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[int] = mapped_column()
    search_id_sub: Mapped[int] = mapped_column()
    document: Mapped[str] = mapped_column()
    create_ymd: Mapped[datetime] = mapped_column()
    download_ymd: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column()

class t_agent_request(Base):
    __tablename__ = "t_agent_request"
    agent_request_id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[int] = mapped_column()
    search_id_sub: Mapped[int] = mapped_column()
    request_ymd: Mapped[datetime] = mapped_column()
    response_ymd: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column()