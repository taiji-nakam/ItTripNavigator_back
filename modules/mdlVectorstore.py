import os
import shutil
import traceback
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import asc
from db_control.connect import engine
from db_control.mymodels import m_talent, talent_job, m_job  # 必要なモデルをインポート
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

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

    # 新規生成
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
                # 追加: talent_job -> m_job をロード
                joinedload(m_talent.jobs).joinedload(talent_job.job)
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
            if talent.careers:
                content += "\n=== 経歴 ===\n"
                for career in talent.careers:
                    content += f"- {career.career_description}\n"
            # マインドセット
            if talent.mindsets:
                content += "\n=== マインドセット ===\n"
                for mindset in talent.mindsets:
                    content += f"- {mindset.mindset_description}\n"
            # 支援領域
            if talent.supportareas:
                content += "\n=== 支援領域 ===\n"
                for supportarea in talent.supportareas:
                    content += f"- {supportarea.supportarea_detail}\n"
            # 追加: 保有職種 (talent_job 経由で m_job.job_name を取得)
            if talent.jobs:
                content += "\n=== 保有職種 ===\n"
                for tjob in talent.jobs:
                    if tjob.job:
                        content += f"- {tjob.job.job_name}\n"

            docs.append(Document(page_content=content.strip()))

        # テキスト分割（長いテキストへの対応）
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
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