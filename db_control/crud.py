from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc, desc, func
import json
import random
import string
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
    m_user,
    t_search,
    d_search, 
    c_user_id,
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

# d_searchデータ追加
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

# m_case リストデータ取得
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

# m_case リスト(代表)データ取得
def select_featured_m_case_list(FEATURED_COUNT) -> Tuple[int, str]:
    """
    1) d_search から case_id をグループ化し、出現回数が多い順に上位 FEATURED_COUNT 件を取得
    2) 取得した case_id が m_case.is_visible=1 の場合のみ事例情報を追加
    3) 不足があれば、m_case の中から is_visible=1 の他の事例を表示順昇順で補い、
       合計 FEATURED_COUNT 件になるようにする
    4) 件数が0なら404、あれば200で返却
    """
    status_code = 200
    result_json = ""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # (1) d_search から case_id ごとの出現回数を集計 (case_id が NULL の行は除外)
        top_case_rows = (
            session.query(
                d_search.case_id,
                func.count(d_search.case_id).label("cnt")
            )
            .filter(d_search.case_id != None)
            .group_by(d_search.case_id)
            .order_by(desc("cnt"))  # 出現回数の多い順
            .limit(FEATURED_COUNT)
            .all()
        )
        # 上位で取得した case_id をリスト化
        top_case_ids = [row.case_id for row in top_case_rows]

        # (2) 上位 case_id の事例情報を取得 (is_visible=1 のみ)
        final_records = []
        if top_case_ids:
            # まず該当する事例情報をまとめて取得
            case_map = (
                session.query(m_case.case_id, m_case.case_name, m_case.case_summary)
                .filter(
                    m_case.is_visible == 1,
                    m_case.case_id.in_(top_case_ids)
                )
                .all()
            )
            # 取得結果を辞書化
            details_dict = {r.case_id: (r.case_name, r.case_summary) for r in case_map}

            # 出現回数の多い順を保ちつつ、final_records に詰める
            for row in top_case_rows:
                c_id = row.case_id
                if c_id in details_dict:  # is_visible=1 の場合のみ
                    final_records.append({
                        "case_id": c_id,
                        "case_name": details_dict[c_id][0],
                        "case_summary": details_dict[c_id][1]
                    })

        # (3) FEATURED_COUNT に満たない場合は、m_case から不足分を補う
        missing_count = FEATURED_COUNT - len(final_records)
        if missing_count > 0:
            # すでに取得済みの case_id を除外
            exclude_ids = [rec["case_id"] for rec in final_records]
            extra = (
                session.query(m_case.case_id, m_case.case_name, m_case.case_summary)
                .filter(m_case.is_visible == 1)
                .filter(~m_case.case_id.in_(exclude_ids))
                .order_by(asc(m_case.display_order))
                .limit(missing_count)
                .all()
            )
            for e in extra:
                final_records.append({
                    "case_id": e.case_id,
                    "case_name": e.case_name,
                    "case_summary": e.case_summary
                })

        # (4) 結果が0件なら404、あれば200
        if not final_records:
            status_code = 404
            result_json = json.dumps({"message": "No featured m_case data available"}, ensure_ascii=False)
        else:
            result_json = json.dumps(final_records, ensure_ascii=False)

        session.commit()
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

# d_searchデータ更新(事例検索用)
def update_d_search_case(
    search_id: int,
    search_id_sub: int,
    param_case_id: int
) -> Tuple[int, Optional[str]]:
    """
    d_searchテーブルのレコードを更新または新規追加し、search_id_sub を返す。
    
    1) (search_id, search_id_sub) で既存レコードを検索
       - 見つからなければ 404 を返す
    2) 見つかったレコードの case_id が null の場合
       - そのレコードを更新して case_id=param_case_id にし、search_id_sub は既存の値のまま
    3) 見つかったレコードの case_id がすでに入っている場合
       - 新規レコードを作成する
         * search_id は同じ
         * search_id_sub は 同一search_id の最大 + 1
         * industry_id, company_size_id, department_id, theme_id, job_id は既存レコードの値をコピー
         * case_id は param_case_id
         * search_ymd はシステム日付
    4) 更新または新規追加したレコードの search_id_sub を返す
    """
    status_code = 200
    return_sub_id: Optional[int] = None

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            # (1) 既存レコードを検索
            current_record = (
                session.query(d_search)
                .filter(
                    d_search.search_id == search_id,
                    d_search.search_id_sub == search_id_sub
                )
                .first()
            )
            if not current_record:
                status_code = 404
                return status_code, f"No d_search record found for search_id: {search_id}, search_id_sub: {search_id_sub}"

            # (2) case_id が null の場合 → 既存レコードを更新
            if current_record.case_id is None:
                current_record.case_id = param_case_id
                session.flush()
                session.refresh(current_record)
                return_sub_id = current_record.search_id_sub

            else:
                # (3) case_id が既に入っている場合 → 新規レコードを作成
                max_sub = (
                    session.query(func.max(d_search.search_id_sub))
                    .filter(d_search.search_id == search_id)
                    .scalar()
                )
                if max_sub is None:
                    new_sub = 1
                else:
                    new_sub = max_sub + 1

                new_record = d_search(
                    search_id=current_record.search_id,
                    search_id_sub=new_sub,
                    industry_id=current_record.industry_id,
                    company_size_id=current_record.company_size_id,
                    department_id=current_record.department_id,
                    theme_id=current_record.theme_id,
                    job_id=current_record.job_id,
                    case_id=param_case_id,
                    search_ymd=datetime.now(ZoneInfo("Asia/Tokyo"))
                )
                session.add(new_record)
                session.flush()
                session.refresh(new_record)
                return_sub_id = new_record.search_id_sub

    except Exception as e:
        session.rollback()
        print("error:", e)
        status_code = 500
        return status_code, str(e)

    finally:
        session.close()

    # (4) 成功時は search_id_sub を返す
    return status_code, str(return_sub_id)

# m_caseデータ取得
def select_m_case(search_id: int, search_id_sub: int) -> Tuple[int, str]:
    """
    1) d_search から (search_id, search_id_sub) をキーに検索し、case_id を取得
       - case_id が NULL or レコードが見つからない場合 → 404エラー
    2) 取得した case_id を使って m_case を検索
       - レコードが見つからない場合 → 404エラー
    3) 取得した m_case のデータ（display_order, is_visible は除外）を JSON 形式で返す
    """
    status_code = 200
    result_json = ""

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1) d_search から case_id を取得
        ds_record = (
            session.query(d_search)
            .filter(
                d_search.search_id == search_id,
                d_search.search_id_sub == search_id_sub
            )
            .first()
        )

        # レコードが無い or case_id が未設定の場合
        if not ds_record or ds_record.case_id is None:
            status_code = 404
            result_json = json.dumps(
                {"message": f"case_id が取得できませんでした for search_id={search_id}, search_id_sub={search_id_sub}"},
                ensure_ascii=False
            )
            return status_code, result_json

        # 2) m_case から事例詳細を取得
        case_record = session.query(m_case).filter(m_case.case_id == ds_record.case_id).first()
        if not case_record:
            status_code = 404
            result_json = json.dumps(
                {"message": f"caseデータが取得できませんでした for case_id={ds_record.case_id}"},
                ensure_ascii=False
            )
            return status_code, result_json

        # 3) 取得した m_case データを JSON に変換 (display_order, is_visible は除外)
        data = {
            "case_id": case_record.case_id,
            "case_name": case_record.case_name,
            "case_summary": case_record.case_summary,
            "company_summary": case_record.company_summary,
            "initiative_summary": case_record.initiative_summary,
            "issue_background": case_record.issue_background,
            "solution_method": case_record.solution_method
        }
        result_json = json.dumps(data, ensure_ascii=False)

    except Exception as e:
        session.rollback()
        status_code = 500
        result_json = json.dumps({"error": "An exception occurred", "details": str(e)}, ensure_ascii=False)
    finally:
        session.close()

    return status_code, result_json

# m_userデータ登録
def insert_m_user(data: "userEntryData") -> Tuple[int, Optional[str]]:
    """
    m_user テーブルへ1件データを挿入し、t_search の user_id を更新する。
      - user_id はランダム英数字5桁 + 連番5桁 (c_user_id の increment_no を加算管理)
      - t_search は data.search_id をキーに検索して user_id を更新
    戻り値: (ステータスコード, JSON文字列 or エラーメッセージ)
    """
    status_code = 200
    result_str: Optional[str] = None

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            # 1) c_user_id テーブルのレコードを取得 (常に1行のみ想定)
            c_record = session.query(c_user_id).first()

            if not c_record:
                # テーブルが空の場合のみ初期レコードを作成
                c_record = c_user_id(increment_no=1)
                session.add(c_record)
                session.flush()
                next_inc = 1
            else:
                # 既存レコードの increment_no をインクリメント
                c_record.increment_no += 1
                session.flush()
                next_inc = c_record.increment_no

            # 2) ランダム英数字(大文字 + 数字) 5桁の生成
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

            # 3) 連番を5桁にゼロ埋め
            seq_str = str(next_inc).zfill(5)

            # 4) user_id の組み立て
            user_id = random_part + seq_str  # 例: ABC12 + 00002 => ABC1200002

            # 5) m_user に新しいユーザを作成
            new_user = m_user(
                user_id=user_id,
                mail_address=data.mail_address or "",
                phone_no=data.phone_no or "",
                company_name=data.company_name or "",
                department_name=data.deparment_name or "",
                job_title=data.job_title or "",
                user_name=data.user_name or "",
                entry_ymd=datetime.now(ZoneInfo("Asia/Tokyo"))
            )
            session.add(new_user)

            # 6) t_search の user_id を更新
            #    data.search_id をキーに t_search を検索し、user_id を更新する
            t_search_record = (
                session.query(t_search)
                .filter(t_search.search_id == data.search_id)
                .first()
            )
            if t_search_record:
                t_search_record.user_id = user_id
                session.flush()

            # 登録完了後に返却するJSONを作成
            result_dict = {
                "user_id": user_id
            }
            result_str = json.dumps(result_dict, ensure_ascii=False)

    except Exception as e:
        session.rollback()
        print("error:", e)
        status_code = 500
        result_str = json.dumps(
            {"error": "An exception occurred.", "details": str(e)},
            ensure_ascii=False
        )
    finally:
        session.close()

    return status_code, result_str