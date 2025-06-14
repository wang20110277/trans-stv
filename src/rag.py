import logging
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 提示词模板
prompt_template = """请根据以下上下文回答最后的问题。如果你不知道答案，请直接说不知道，切勿编造答案。回答应简洁明了，最多使用三句话，确保直接针对问题，并鼓励提问者提出更多问题。

{context}

问题：{question}

有帮助的答案："""

class Rag:
    _instance = None

    def __new__(cls, config: dict = None):
        if cls._instance is None:
            cls._instance = super(Rag, cls).__new__(cls)
            cls._instance.init(config)  # 初始化实例属性
        return cls._instance

    def init(self, config: dict):
        """初始化 RAG 实例"""
        self._validate_config(config)
        self.doc_path = config["doc_path"]
        self.emb_model = config["emb_model"]
        self.ollama_url = config["url"]
        self.model_name = config["model_name"]

        # 初始化提示词模板
        self.custom_rag_prompt = PromptTemplate.from_template(prompt_template)

        # 加载文档并初始化向量存储
        self.vector_store = self._initialize_vector_store()
        self.retriever = self.vector_store.as_retriever()

        # 初始化 RAG 链
        self.rag_chain = self._initialize_rag_chain()

    def _validate_config(self, config: dict):
        """验证配置参数"""
        required_keys = ["doc_path", "emb_model", "url", "model_name"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

    def _initialize_vector_store(self):
        """加载文档并初始化向量存储"""
        try:
            # 定义加载器，支持不同文档类型
            loader = DirectoryLoader(
                self.doc_path,
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()

            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)

            # 初始化嵌入模型
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            embedding_model = HuggingFaceBgeEmbeddings(
                model_name=self.emb_model,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )

            # 创建向量存储
            return Chroma.from_documents(documents=splits, embedding=embedding_model)
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def _initialize_rag_chain(self):
        """初始化 RAG 链"""
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        return (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.custom_rag_prompt
            | self.ollama_llm
            | StrOutputParser()
        )

    def ollama_llm(self, prompt: str):
        """调用本地 ollama 服务的 LLM 生成回答"""
        try:
            url = f"{self.ollama_url}/api/chat"
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            response = requests.post(url, json=data, stream=False)
            response.raise_for_status()
            response_data = response.json()
            # 使用正则表达式过滤掉<think>和</think>之间的内容
            filtered_text = re.sub(r'<think>.*?</think>', '', response_data["message"]["content"], flags=re.DOTALL)

            # 去除多余的换行符
            filtered_text = filtered_text.strip()
            # 定义需要替换的特殊字符
            special_chars = {
                "*": "",  # 替换为空格
                "《": "",  # 删除
                "》": "",  # 删除
                "～": "",  # 删除
            }
            # 逐个替换特殊字符
            for char, replacement in special_chars.items():
                filtered_text = filtered_text.replace(char, replacement)

            return filtered_text
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return f"Error in response generation: {e}"

    def query(self, query: str):
        """执行查询并返回结果"""
        try:
            result = self.rag_chain.invoke(query)
            return f"帮你找到: {query} 相关的信息，" + str(result)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return f"Error executing query: {e}"


if __name__ == "__main__":
    # 配置
    config = {
        "doc_path": "../documents/",  # 替换为你的文档路径
        "emb_model": "../models/bge-small-zh",  # 替换为你的嵌入模型
        "url": "http://localhost:11434",  # ollama 服务地址
        "model_name": "deepseek-r1:14b"  # ollama 模型名称
    }

    # 初始化 RAG 实例
    rag = Rag(config)

    # 执行查询
    query = "什么是 RAG？"
    result = rag.query(query)
    print(result)