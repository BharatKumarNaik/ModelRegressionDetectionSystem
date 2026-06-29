"""
Builds the FAISS vector store used to retrieve relevant table-schema
context for a given natural-language question.
"""
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config.settings import EMBEDDING_MODEL, RETRIEVER_TOP_K
from src.utils.logger import logging


def build_vector_store(documents: List[Document]) -> FAISS:
    logging.info("build vector store")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    return FAISS.from_documents(documents, embeddings)


def get_schema_retriever(vector_db: FAISS, k: int = RETRIEVER_TOP_K):
    logging.info("get schema retriever function")
    return vector_db.as_retriever(search_kwargs={"k": k})


def combine_documents(docs: List[Document]) -> str:
    logging.info("combine documents function")
    return "\n\n".join(doc.page_content for doc in docs)
