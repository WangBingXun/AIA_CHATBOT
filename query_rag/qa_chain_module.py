# -*- coding: utf-8 -*-
"""qa_chain_module.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Y7p1grfmLk06ZJo3mVCBWWt6YOlSC2Xh
"""

# qa_chain_module.py
# 首先，建立RAG流程使用的embedding model，並連線至AIA PrimeHub vectorDB
# 接著，建立兩個LLM Model服務與retriever，建立PromptTemplate for RetrievalQA
# 最後，建立RetrievalQA : 提供前端query至pipeline.query()

import os
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama

class QARetrievalPipeline:
    def __init__(self, collection_name: str, nomic_api_key: str, chroma_host: str, chroma_port: int,
                 groq_api_key: str, groq_model_name: str, ollama_model: str, ollama_base_url: str):
        # 初始化 Embedding 模型
        os.environ['NOMIC_API_KEY'] = nomic_api_key
        self.embedding = NomicEmbeddings(model="nomic-embed-text-v1.5")

        # 初始化 Chroma 数据库连接
        http_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(
                chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider",
                chroma_client_auth_credentials="admin:admin"
            )
        )

        self.db = Chroma(
            client=http_client,
            collection_name=collection_name,
            embedding_function=self.embedding
        )

        # 初始化 Groq LLM 服务
        self.llm_Groq_llama3 = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name=groq_model_name
        )

        # 初始化 PrimeHub Ollama LLM 服务
        self.llm_primehub_llama3 = Ollama(
            model=ollama_model,
            base_url=ollama_base_url
        )

        # 初始化 Retriever
        self.retriever = self.db.as_retriever(search_kwargs={
            "fetch_k": 10,
            "k": 3,
            "mmr_score_cache": True,
            "mmr_rerank_top_k": 30
        }, retriever_mode="reduce_op_recursive", search_type="mmr")


        # 定义 PromptTemplate
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Use the following pieces of context to answer the question at the end. Please answer in Chinese. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""
        )

    def set_llm(self, use_primehub: bool = False):
        """选择要使用的 LLM 模型，默认使用 Groq 模型。"""
        if use_primehub:
            self.llm = self.llm_primehub_llama3
        else:
            self.llm = self.llm_Groq_llama3

        # 使用新选择的 LLM 初始化 RetrievalQA
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
            chain_type="stuff",
            chain_type_kwargs={"prompt": self.qa_prompt}
        )

    def query(self, question: str):
        # 使用 qa_chain 查询
        return self.qa_chain({"query": question})


# qa_chain_module.py 使用示例（外部調用時）
from qa_chain_module import QARetrievalPipeline

# 初始化流水線，傳入必要的参数
pipeline = QARetrievalPipeline(
    collection_name="xt131028_v1",
    nomic_api_key="nk-BCjzlgQXfYdZNA6kUZ-6Jeq1NIG2JhlQJaTe9BedpDc", #換成自己的nomic_api_key
    chroma_host="64.176.47.89",
    chroma_port=8000,
    groq_api_key="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",#換成自己的groq_api_key
    groq_model_name="llama3-8b-8192",
    ollama_model="llama3",
    ollama_base_url="http://8cf8-140-109-17-45.ngrok-free.app" # 設定自建的LLM服務位置
)

# 選擇要使用的 LLM 模型（True 使用 PrimeHub Ollama 模型，False 使用 Groq 模型）
pipeline.set_llm(use_primehub=True)

# 提供前端query至pipeline.query
question = "摘要技術領袖全域班的課程內容"
response = pipeline.query(question)
print(response)