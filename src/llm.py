from abc import ABC, abstractmethod
import json
import re
import requests
import logging
from langchain_experimental.llms.ollama_functions import OllamaFunctions

logger = logging.getLogger(__name__)

class LLM(ABC):
    @abstractmethod
    def response(self, dialogue):
        pass

class OllamaLLM(LLM):
    def __init__(self, config):
        # 从配置中获取参数
        self.model_name = config.get("model_name")
        self.url = config.get("url")  # 默认 URL

    def response(self, dialogue):
        try:
            # 构造请求 URL
            url = f"{self.url}/api/chat"
            data = {
                "model": self.model_name,
                "messages": dialogue,
                "stream": False
            }

            # 发送请求
            response = requests.post(url, json=data, stream=False)
            response.raise_for_status()  # 检查请求是否成功

            # 返回响应内容
            for chunk in response.iter_lines():
                if chunk:
                    chunk_data = chunk.decode("utf-8")
                    # 解析 JSON 数据
                    parsed_data = json.loads(chunk_data)

                    # 提取 parsed_data["message"]["content"] 值
                    # print(parsed_data["message"]["content"])

                    # 使用正则表达式过滤掉<think>和</think>之间的内容
                    filtered_text = re.sub(r'<think>.*?</think>', '', parsed_data["message"]["content"], flags=re.DOTALL)

                    # 去除多余的换行符
                    filtered_text = filtered_text.strip()

                    # 定义需要替换的特殊字符
                    special_chars = {
                        "*": "",  # 替换为空格
                        "《": "",  # 删除
                        "》": "",  # 删除
                        "～": "~",  # 替换为普通波浪号
                    }

                    # 逐个替换特殊字符
                    for char, replacement in special_chars.items():
                        filtered_text = filtered_text.replace(char, replacement)
                    # print(filtered_text)

                    yield filtered_text
        except Exception as e:
            logger.error(f"Error in response generation: {e}")

    def response_call(self, dialogue, functions_call):
        try:
            # 构造请求 URL
            url = f"{self.url}/api/chat"
            data = {
                "model": self.model_name,
                "messages": dialogue,
                "stream": False,
                "tools": functions_call
            }

            # 发送请求
            response = requests.post(url, json=data, stream=False)
            response.raise_for_status()  # 检查请求是否成功

            # 返回响应内容
            for chunk in response.iter_lines():
                if chunk:
                    chunk_data = chunk.decode("utf-8")
                    # 解析 JSON 数据
                    parsed_data = json.loads(chunk_data)
                    # 提取 parsed_data["message"]["content"] 值
                    print(parsed_data["message"]["content"])

                    # 使用正则表达式过滤掉<think>和</think>之间的内容
                    filtered_text = re.sub(r'<think>.*?</think>', '', parsed_data["message"]["content"],
                                           flags=re.DOTALL)

                    # 去除多余的换行符
                    filtered_text = filtered_text.strip()
                    # 定义需要替换的特殊字符
                    special_chars = {
                        "*": "",  # 替换为空格
                        "《": "",  # 删除
                        "》": "",  # 删除
                        "～": "~",  # 替换为普通波浪号
                    }

                    # 逐个替换特殊字符
                    for char, replacement in special_chars.items():
                        filtered_text = filtered_text.replace(char, replacement)
                    # 提取 filtered_text,parsed_data["message"]["tool_calls"] 值
                    print(filtered_text,parsed_data["message"]["tool_calls"])
                    yield filtered_text,parsed_data["message"]["tool_calls"]
        except Exception as e:
            logger.error(f"Error in response generation: {e}")

def create_instance(class_name, *args, **kwargs):
    # 获取类对象
    cls = globals().get(class_name)
    if cls:
        # 创建并返回实例
        return cls(*args, **kwargs)
    else:
        raise ValueError(f"Class {class_name} not found")


if __name__ == "__main__":
    # 配置
    config = {
        "model_name": "deepseek-r1:14b",
        "url": "http://localhost:11434",
        "api_key": None  # 如果没有 API Key，可以设置为 None
    }

    # 创建 OllamaLLM 的实例
    ollama = create_instance("OllamaLLM", config)
    dialogue = [{"role": "user", "content": "你是谁"}]

    # 打印逐步生成的响应内容
    for chunk in ollama.response(dialogue):
        print(chunk)

