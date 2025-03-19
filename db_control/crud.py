# uname() error回避
import platform
import math
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc,func
import json
import pandas as pd
from datetime import datetime
from typing import Tuple, Optional
from zoneinfo import ZoneInfo
from db_control.connect import engine
from db_control.mymodels import (
    m_industry,
    m_company_size,
    m_department,
    m_theme,
    m_case,
    t_search,
    d_search, 
    case_industry, 
    case_company_size,
    case_department,
    case_theme
)
from models.params import caseSearchData

# m_industryデータ取得
def select_m_industry() -> Tuple[int, str]:
    # 初期化
    result_json = ""
    status_code = 200

    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # クエリの作成: is_visible = 1 のデータを display_order 順に取得
        result = (
            session.query(m_industry.industry_id, m_industry.industry_name)
            .filter(m_industry.is_visible == 1)
            .order_by(asc(m_industry.display_order))
            .all()
        )
        
        # 結果をチェック
        if not result:
            result_json = json.dumps({"message": "Industry not found"}, ensure_ascii=False)
            status_code = 404
        else:
            # クエリ結果をリスト形式で JSON に変換
            result_json = json.dumps(
                [{"industry_id": industry_id, "industry_name": industry_name} for industry_id, industry_name in result],
                ensure_ascii=False
            )

    except Exception as e:
        result_json = json.dumps(
            {"error": "例外が発生しました。", "details": str(e)}, 
            ensure_ascii=False
        )
        print("!!error!!", e)
        status_code = 500
    finally:
        # セッションを閉じる
        session.close()

    return status_code, result_json

# m_company_sizeデータ取得
def select_m_company_size() -> Tuple[int, str]:
    # 初期化
    result_json = ""
    status_code = 200

    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # クエリの作成: is_visible = 1 のデータを display_order 順に取得
        result = (
            session.query(
                m_company_size.company_size_id,
                m_company_size.company_size_name
            )
            .filter(m_company_size.is_visible == 1)
            .order_by(asc(m_company_size.display_order))
            .all()
        )

        # 結果をチェック
        if not result:
            result_json = json.dumps({"message": "Company size not found"}, ensure_ascii=False)
            status_code = 404
        else:
            # クエリ結果をリスト形式で JSON に変換
            result_json = json.dumps(
                [
                    {"company_size_id": company_size_id, "company_size_name": company_size_name}
                    for company_size_id, company_size_name in result
                ],
                ensure_ascii=False
            )

    except Exception as e:
        result_json = json.dumps({"error": "例外が発生しました。", "details": str(e)}, ensure_ascii=False)
        print("!!error!!", e)
        status_code = 500
    finally:
        # セッションを閉じる
        session.close()

    return status_code, result_json

# m_departmentデータ取得
def select_m_department() -> Tuple[int, str]:
    # 初期化
    result_json = ""
    status_code = 200

    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # クエリの作成: is_visible = 1 のデータを display_order 順に取得
        result = (
            session.query(
                m_department.department_id,
                m_department.department_name
            )
            .filter(m_department.is_visible == 1)
            .order_by(asc(m_department.display_order))
            .all()
        )

        # 結果をチェック
        if not result:
            result_json = json.dumps({"message": "Department not found"}, ensure_ascii=False)
            status_code = 404
        else:
            # クエリ結果をリスト形式で JSON に変換
            result_json = json.dumps(
                [
                    {"department_id": department_id, "department_name": department_name}
                    for department_id, department_name in result
                ],
                ensure_ascii=False
            )

    except Exception as e:
        result_json = json.dumps({"error": "例外が発生しました。", "details": str(e)}, ensure_ascii=False)
        print("!!error!!", e)
        status_code = 500
    finally:
        # セッションを閉じる
        session.close()

    return status_code, result_json

# m_themeデータ取得
def select_m_theme() -> Tuple[int, str]:
    # 初期化
    result_json = ""
    status_code = 200

    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # クエリの作成: is_visible = 1 のデータを display_order 順に取得
        result = (
            session.query(
                m_theme.theme_id,
                m_theme.theme_name
            )
            .filter(m_theme.is_visible == 1)
            .order_by(asc(m_theme.display_order))
            .all()
        )

        # 結果をチェック
        if not result:
            result_json = json.dumps({"message": "Theme not found"}, ensure_ascii=False)
            status_code = 404
        else:
            # クエリ結果をリスト形式で JSON に変換
            result_json = json.dumps(
                [
                    {"theme_id": theme_id, "theme_name": theme_name}
                    for theme_id, theme_name in result
                ],
                ensure_ascii=False
            )
    except Exception as e:
        result_json = json.dumps({"error": "例外が発生しました。", "details": str(e)}, ensure_ascii=False)
        print("!!error!!", e)
        status_code = 500
    finally:
        # セッションを閉じる
        session.close()

    return status_code, result_json

# t_searchデータ追加
def insert_search(search_mode: int) -> Tuple[int, Optional[int]]:
    """
    t_searchテーブルに1件データを挿入する。
    - search_id : 自動採番
    - user_id   : NULL
    - search_ymd: システム日付(時分秒)
    - search_mode: 引数で受け取る
    
    戻り値:
      (ステータスコード, search_id)
      ※例外が起きた場合は search_id=None
    """
    status_code = 200
    inserted_id: Optional[int] = None

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            # 新しい検索履歴データを生成
            new_search = t_search(
                user_id=None,  # NULL
                search_ymd=datetime.now(ZoneInfo("Asia/Tokyo")),
                search_mode=search_mode
            )
            session.add(new_search)

            # flush & refresh で自動採番されたIDを取得
            session.flush()
            session.refresh(new_search)
            inserted_id = new_search.search_id

    except Exception as e:
        session.rollback()
        print("error:", e)
        status_code = 500
    finally:
        session.close()

    return status_code, inserted_id

def insert_d_search(data: caseSearchData) -> Tuple[int, Optional[int]]:
    """
    d_search テーブルへ1件データを挿入する。
      - 同一の data.search_id の中で、最大の search_id_sub + 1 を新しい search_id_sub に設定する
      - 同一の data.search_id のレコードが存在しない場合は、search_id_sub = 1 とする
      - job_id, case_id は NULL、search_ymd はシステム日時
    挿入後、作成された search_id_sub をそのまま返す。
    
    戻り値:
      (ステータスコード, search_id_sub)
    """
    status_code = 200
    inserted_sub_id: Optional[int] = None

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            # 同一 search_id のレコードの中で、最大の search_id_sub を取得
            max_sub = session.query(func.max(d_search.search_id_sub))\
                             .filter(d_search.search_id == data.search_id)\
                             .scalar()
            if max_sub is None:
                new_sub = 1
            else:
                new_sub = max_sub + 1

            # 新しいレコードの作成
            new_record = d_search(
                search_id=data.search_id,
                search_id_sub=new_sub,  # 計算した値を設定
                industry_id=data.industry_id,
                company_size_id=data.company_size_id,
                department_id=data.department_id,
                theme_id=data.theme_id,
                case_id=None,  # NULL を設定
                job_id=None,   # NULL を設定
                search_ymd=datetime.now(ZoneInfo("Asia/Tokyo"))
            )
            session.add(new_record)
            session.flush()
            session.refresh(new_record)
            inserted_sub_id = new_record.search_id_sub

    except Exception as e:
        session.rollback()
        print("error:", e)
        status_code = 500
    finally:
        session.close()

    return status_code, inserted_sub_id

def select_m_case_list(search_id: Optional[int], search_id_sub: Optional[int]) -> Tuple[int, str]:
    """
    1) d_search から (search_id, search_id_sub) をキーに1件取得
    2) 取得した industry_id, company_size_id, department_id, theme_id が Null でなければ
       対応する事例対応表 (case_industry 等) と JOIN して m_case を絞り込み
    3) m_case.is_visible = 1 のみ
    4) display_order 昇順で事例ID, 事例名, 事例概要を取得
    5) 結果が無ければ 404, あれば 200
    """

    Session = sessionmaker(bind=engine)
    session = Session()

    status_code = 200
    result_json = ""

    try:
        # 1) d_search から業界ID等を取得
        ds = (
            session.query(d_search)
            .filter(
                d_search.search_id == search_id,
                d_search.search_id_sub == search_id_sub
            )
            .first()
        )

        if not ds:
            status_code = 404
            result_json = json.dumps({"message": "No d_search record found"}, ensure_ascii=False)
            return status_code, result_json

        # 2) m_case をベースにクエリを作成 (事例ID, 事例名, 事例概要のみ取得)
        query = (
            session.query(
                m_case.case_id,
                m_case.case_name,
                m_case.case_summary
            )
            .filter(m_case.is_visible == 1)  # is_visible=1 のみ
        )

        # industry_id が Null でなければ JOIN + 絞り込み
        if ds.industry_id is not None:
            query = (
                query.join(case_industry, m_case.case_id == case_industry.case_id)
                     .filter(case_industry.industry_id == ds.industry_id)
            )

        # company_size_id が Null でなければ
        if ds.company_size_id is not None:
            query = (
                query.join(case_company_size, m_case.case_id == case_company_size.case_id)
                     .filter(case_company_size.company_size_id == ds.company_size_id)
            )

        # department_id が Null でなければ
        if ds.department_id is not None:
            query = (
                query.join(case_department, m_case.case_id == case_department.case_id)
                     .filter(case_department.department_id == ds.department_id)
            )

        # theme_id が Null でなければ
        if ds.theme_id is not None:
            query = (
                query.join(case_theme, m_case.case_id == case_theme.case_id)
                     .filter(case_theme.theme_id == ds.theme_id)
            )

        # 3) display_order 昇順
        query = query.order_by(asc(m_case.display_order))

        # 4) 結果取得
        records = query.all()

        if not records:
            status_code = 404
            result_json = json.dumps({"message": "No m_case data available"}, ensure_ascii=False)
        else:
            # JSONに整形
            result_list = []
            for row in records:
                case_id, case_name, case_summary = row
                result_list.append({
                    "case_id": case_id,
                    "case_name": case_name,
                    "case_summary": case_summary
                })
            result_json = json.dumps(result_list, ensure_ascii=False)

    except Exception as e:
        session.rollback()
        status_code = 500
        result_json = json.dumps(
            {"error": "An exception occurred.", "details": str(e)},
            ensure_ascii=False
        )
    finally:
        session.close()

    return status_code, result_json