# ユーザ向けアクションモジュール
import json
from models.params import  userEntryData, userData
from db_control import crud
from fastapi import HTTPException
import os
import smtplib
from email.message import EmailMessage

# ユーザー情報を登録
def createUser(data:userEntryData) -> tuple[int, str]:

    # ユーザー情報を登録
    status, result = crud.insert_m_user(data)

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

    return status, result

# エージェント相談情報を登録し担当へメール通知
def createRequest(data:userData) -> tuple[int, str]:

    # ユーザーリクエスト情報を登録
    status, result = crud.insert_t_agent_request(data)

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

    # 環境変数から設定を取得
    MAIL_USER = os.getenv("MAIL_USER")            # 例: "2@gmail.com"
    MAIL_PASS = os.getenv("MAIL_PASS")            # 例: "hogehoge"
    MSG_SUBJECT = os.getenv("MSG_SUBJECT")        # 例: "[ITTripNavi]新しいエージェント相談希望がありました"
    MSG_MAIN = os.getenv("MSG_MAIN")              # 例: "新しいエージェント相談が登録されました。以下のリクエストIDの情報を確認してください。"
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")  # 例: "1@gmail.com"

    # EmailMessage を生成
    msg = EmailMessage()
    msg['Subject'] = MSG_SUBJECT      # EmailMessage は自動でエンコーディング処理してくれます
    msg['From'] = MAIL_USER
    msg['To'] = NOTIFICATION_EMAIL
    msg.set_content(f"{MSG_MAIN}\nリクエストID : {result}")
    # Mail送信
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_USER, MAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        print("メール送信エラー:", e)

    return status, result