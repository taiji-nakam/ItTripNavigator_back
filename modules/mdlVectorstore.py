import os
import shutil
import traceback
import json
import vectorstore_global
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import asc, true
from db_control.connect import engine
from db_control.mymodels import m_talent, talent_job, m_job, talent_hashtag, m_hashtag  # 必要なモデルをインポート
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS


def createVectorstore(target: str) -> tuple[int, str]:
    """
    VectorStoreを再作成する
    2025/04/05現在 talentのみ対応
    """

    if target == "talent":
        # talent_Vectorstoreを強制的に作成する
        vectorstore = create_talent_vectorstore(true)
        if vectorstore is not None:
            vectorstore_global.talent_vectorstore = vectorstore
            result = {"message": "Vectorstore created successfully."}
            return 200, json.dumps(result, ensure_ascii=False)
        else:
            result = {"message": "Vectorstore creation failed."}
            return 500, json.dumps(result, ensure_ascii=False)
    else:
        result = {"message": f"対象 '{target}' が見つかりません。"}
        return 404, json.dumps(result, ensure_ascii=False)

def create_talent_vectorstore(force_recreate: bool = False):
    """
    m_talentテーブルを中心に、関連テーブルの情報（経歴、マインドセット、支援領域、職種情報）を取得し、
    Document化、テキスト分割を行った後、FAISS インデックスを生成する関数です。

    パラメータ force_recreate が True の場合、既存のインデックス保存ディレクトリがあれば削除して再生成します。
    また、環境変数 DO_GPT が "TRUE" の場合のみ OpenAI API を利用してベクトル化を行います。
    """
    index_dir = "rag/talent_vectorstore_index"
    DO_GPT = os.getenv("DO_GPT")
    OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")

    # 強制再生成の場合、既存のインデックスディレクトリを削除
    if force_recreate and os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print(f"[vectorstore.py] force_recreate=True のため、既存のインデックスディレクトリ '{index_dir}' を削除しました。")

    # インデックスが既に存在する場合はロードを試みる
    if os.path.exists(index_dir):
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            talent_vectorstore = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
            print(f"[vectorstore.py] ディスクから talent_vectorstore をロードしました (ディレクトリ: '{index_dir}')")
            return talent_vectorstore
        except Exception as e:
            print("ディスクからの talent_vectorstore ロード時にエラーが発生しました:", e)
            traceback.print_exc()
            # ロードに失敗した場合は再生成を試みる

    #  新規生成
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # m_talent と関連テーブルをまとめて取得
        talents = (
            session.query(m_talent)
            .options(
                joinedload(m_talent.careers),
                joinedload(m_talent.mindsets),
                joinedload(m_talent.supportareas),
                joinedload(m_talent.jobs).joinedload(talent_job.job),
                # 追加: talent_hashtag -> m_hashtag をロード
                joinedload(m_talent.hashtags).joinedload(talent_hashtag.hashtag)
            )
            .filter(m_talent.is_visible == True)
            .order_by(asc(m_talent.display_order))
            .all()
        )

        docs = []
        for talent in talents:
            content = f"""\
【名前】
{talent.name}

【エグゼクティブサマリー】
{talent.summary}

【業界情報】
{talent.industry}
"""
            # 経歴
            content += "\n=== 経歴 ===\n"
            if talent.careers:
                career_lines = [f"- {career.career_description}\n" for career in talent.careers ]
                if career_lines:
                    content += "".join(career_lines)
                else:
                    content += "なし\n"
            else:
                content += "なし\n"

            # マインドセット
            content += "\n=== マインドセット ===\n"
            if talent.mindsets:
                mindset_lines = [f"- {mindset.mindset_description}\n" for mindset in talent.mindsets ]
                if mindset_lines:
                    content += "".join(mindset_lines)
                else:
                    content += "なし\n"
            else:
                content += "なし\n"

            # 支援領域
            content += "\n=== 支援領域 ===\n"
            if talent.supportareas:
                supportarea_lines = [f"- {supportarea.supportarea_detail}\n" for supportarea in talent.supportareas ]
                if supportarea_lines:
                    content += "".join(supportarea_lines)
                else:
                    content += "なし\n"
            else:
                content += "なし\n"

            # 保有職種 (talent_job 経由で m_job.job_name を取得)
            content += "\n=== 保有職種 ===\n"
            if talent.jobs:
                job_lines = [f"- {tjob.job.job_name}\n" for tjob in talent.jobs if tjob.job]
                if job_lines:
                    content += "".join(job_lines)
                else:
                    content += "なし\n"
            else:
                content += "なし\n"

            # ハッシュタグ (talent_hashtag 経由で m_hashtag.hashtag_name を取得)
            content += "\n=== ハッシュタグ ===\n"
            if talent.hashtags:
                hashtag_lines = [f"- {th.hashtag.hashtag_name}\n" for th in talent.hashtags if th.hashtag]
                if hashtag_lines:
                    content += "".join(hashtag_lines)
                else:
                    content += "なし\n"
            else:
                content += "なし\n"

            docs.append(Document(page_content=content.strip()))

        # テキスト分割（長いテキストへの対応）
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=150)
        split_docs = text_splitter.split_documents(docs)

        if DO_GPT == "TRUE":
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            talent_vectorstore = FAISS.from_documents(split_docs, embeddings)
            # 生成したインデックスをディスクに保存
            talent_vectorstore.save_local(index_dir)
            print(f"[vectorstore.py] 新規に talent_vectorstore を生成し、ディスクに保存しました (ディレクトリ: '{index_dir}')。 件数: {len(split_docs)}")
            return talent_vectorstore
        else:
            print("[vectorstore.py] DO_GPT が TRUE ではないため、OpenAI API を使用したベクトルストア生成をスキップしました。")
            return None
    except Exception as e:
        print("talent_vectorstore 生成時にエラーが発生しました:", e)
        traceback.print_exc()
        return None
    finally:
        session.close()