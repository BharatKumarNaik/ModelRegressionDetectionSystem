"""
Prompt templates used by the agent chain. Kept separate from chains.py so
prompt wording can be iterated on without touching orchestration logic.
"""
from langchain_core.prompts import ChatPromptTemplate

sql_prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are a SQL Server expert. 
     Generate ONLY the raw executable SQL script based on the question. 
     Do not include markdown formatting, explanations, or backticks.
     """),
    ("human", "database schema and Table Relationship Details:{schema_context}\n ***question: {question}***")
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system","You are a precise data assistant. Answer the user's question directly and completely using only the provided database context records."),
    ("human","Database Context:\n{sql_result}\n\nQuestion: {question}")
])
