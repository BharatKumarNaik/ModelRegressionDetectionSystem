"""
Builds the FAISS vector store used to retrieve relevant table-schema
context for a given natural-language question.
"""
from typing import List
import os,sys
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config.settings import EMBEDDING_MODEL, RETRIEVER_TOP_K,VECTOR_STORE_DIR
from src.utils.logger import logging
from src.utils.exception import MRDException


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    try:
        return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    except Exception as e:
        raise MRDException(e,sys) from e   

def build_vector_store(documents: List[Document]) -> FAISS:
    try:
        logging.info("build vector store")
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        return FAISS.from_documents(documents, embeddings)
    except Exception as e:
        raise MRDException(e,sys) from e

def save_vector_store(vector_db: FAISS, path: str = VECTOR_STORE_DIR) -> None:
    try:
        os.makedirs(path, exist_ok=True)
        vector_db.save_local(path)
        logging.info("Saved FAISS vector store to %s", path)
    except Exception as e:
        raise MRDException(e,sys) from e

def load_vector_store(path: str = VECTOR_STORE_DIR) -> FAISS:
    try:
        logging.info("Loading existing FAISS vector store from %s", path)
        embeddings = _get_embeddings()
        # allow_dangerous_deserialization is safe here because we only ever
        # load index files that this same codebase wrote to local disk.
        return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        raise MRDException(e,sys) from e


def vector_store_exists(path: str = VECTOR_STORE_DIR) -> bool:
    try:
        return os.path.exists(os.path.join(path, "index.faiss")) and os.path.exists(
            os.path.join(path, "index.pkl")
        )
    except Exception as e:
        raise MRDException(e,sys) from e


def get_schema_retriever(vector_db: FAISS, k: int = RETRIEVER_TOP_K):
    try:
        logging.info("get schema retriever function")
        return vector_db.as_retriever(search_kwargs={"k": k})
    except Exception as e:
        raise MRDException(e,sys) from e


def combine_documents(docs: List[Document]) -> str:
    try:
        logging.info("combine documents function")
        return "\n\n".join(doc.page_content for doc in docs)
    except Exception as e:
        raise MRDException(e,sys) from e
