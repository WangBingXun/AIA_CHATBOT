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
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor, LLMChainFilter
from langchain.retrievers.multi_query import MultiQueryRetriever
import time
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

# 設定的embedding 模型
from typing import List
from sentence_transformers import SentenceTransformer
class Stella_Base_zh_v3_1792d:
    def __init__(self, model):
        self.model = SentenceTransformer(model, trust_remote_code=True)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.model.encode(t).tolist() for t in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode([query]).tolist()[0]


class QARetrievalPipeline:
    def __init__(self, collection_name: str, nomic_api_key: str, chroma_host: str, chroma_port: int,
                 groq_api_key: str, groq_model_name: str, ollama_model: str, ollama_base_url: str,
                 openai_api_key: str, openai_model_name: str):

        # 初始化 Embedding 模型
        os.environ['NOMIC_API_KEY'] = nomic_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
        self.embedding = NomicEmbeddings(model="nomic-embed-text-v1.5")
        self.StellaEmbeddings = Stella_Base_zh_v3_1792d('infgrad/stella-base-zh-v3-1792d')
        if openai_api_key and openai_api_key != "":
            self.Ada002Embedding = OpenAIEmbeddings()

        # 初始化 Chroma 数据库连接
        http_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(
                chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider",
                chroma_client_auth_credentials="admin:admin"
            )
        )

        #依據collection name 判斷需要用哪一個模型
        is_NomicEmbeddings = collection_name in ("xt131028","xt131028_v1","nomic_250_18admission_and_qa","nomic_400_18admission_and_qa")
        is_StellaEmbeddings = collection_name in ("xt131028_v1.2","stella_250_18admission_and_qa","stella_400_18admission_and_qa")
        is_GptAada002_Embedding = collection_name in ("gptada002_400_18admission_and_qa")

        if is_NomicEmbeddings:
          db_embedding_function = self.embedding
        elif is_StellaEmbeddings:
          db_embedding_function = self.StellaEmbeddings
        else:
          db_embedding_function = self.Ada002Embedding

        # 建立 collection 連線
        self.db = Chroma(
            client=http_client,
            collection_name=collection_name,
            embedding_function= db_embedding_function
        )

        # 初始化 Groq LLM 服务
        self.llm_Groq = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name=groq_model_name
        )

        # 初始化 PrimeHub Ollama LLM 服务
        self.llm_primehub = Ollama(
            model=ollama_model,
            base_url=ollama_base_url
        )

        #初始化 OpenAI LLM 服务
        if openai_api_key and openai_api_key != "":
            self.llm_OpenAI = ChatOpenAI(
                model_name=openai_model_name,
                temperature=0
            )


        # 初始化基本 Retriever
        self.retriever = self.db.as_retriever(search_kwargs={
            "fetch_k": 10,
            "k": 10,
            "mmr_score_cache": True,
            "mmr_rerank_top_k": 30
        }, retriever_mode="reduce_op_recursive", search_type="mmr")

        # 初始化两种 Contextual Compression Retriever
        extractor = LLMChainExtractor.from_llm(self.llm_primehub)
        self.compression_retriever_1 = ContextualCompressionRetriever(
            base_compressor=extractor,
            base_retriever=self.retriever
        )

        filter_ = LLMChainFilter.from_llm(self.llm_primehub)
        self.compression_retriever_2 = ContextualCompressionRetriever(
            base_compressor=filter_,
            base_retriever=self.retriever
        )

        # 初始化 MultiQuery Retriever
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=self.db.as_retriever(),
            llm=self.llm_primehub
        )

        # 定义 PromptTemplate
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Use the following pieces of context to answer the question at the end. Please answer in Chinese. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
                    {context}
                    Question: {question}
                    Helpful Answer:"""
                            )

    def set_llm(self, use_groq: bool = False, use_primehub: bool = False, use_openai: bool = False):
        """选择要使用的 LLM 模型，默认使用 Groq 模型。"""
        if use_openai:
            self.llm = self.llm_OpenAI
        elif use_primehub:
            self.llm = self.llm_primehub
        else:
            self.llm = self.llm_Groq

        # 使用新选择的 LLM 初始化 QA 链（Retriever 由外部选择）
        self._init_qa_chain(self.retriever)

    def set_retriever(self, retriever_type: str = "default"):
        """选择使用的检索器类型，默认使用基础 Retriever。"""
        if retriever_type == "compression_1":
            retriever = self.compression_retriever_1
        elif retriever_type == "compression_2":
            retriever = self.compression_retriever_2
        elif retriever_type == "multi_query":
            retriever = self.multi_query_retriever
        else:
            retriever = self.retriever

        # 根据选择的检索器重新初始化 QA 链
        self._init_qa_chain(retriever)

    def _init_qa_chain(self, retriever):
        """内部方法，用于根据指定的检索器初始化 QA 链。"""
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type="stuff",
            chain_type_kwargs={"prompt": self.qa_prompt}
        )

    def query(self, question: str):
        """使用当前设置的 QA 链进行查询。"""
        # time.sleep(180)  # 等待180秒再發送下一個請求 (跑 Groq 的 llama3-70b 才需要)
        return self.qa_chain({"query": question})
