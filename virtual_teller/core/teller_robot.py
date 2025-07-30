"""
虚拟柜员机器人核心模块
基于原有的Robot类，针对银行业务场景进行专门优化
"""

import json
import queue
import threading
import uuid
from abc import ABC
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from src import (
    recorder,
    player,
    asr,
    llm,
    tts,
    vad,
    memory,
    rag
)
from src.dialogue import Message, Dialogue
from src.utils import is_interrupt, read_config, is_segment, extract_json_from_string
from plugins.registry import Action
from plugins.task_manager import TaskManager
from virtual_teller.banking.bank_operations import BankOperations
from virtual_teller.security.compliance_checker import ComplianceChecker

logger = logging.getLogger(__name__)

# 虚拟柜员系统提示词
banking_sys_prompt = """
# 角色定义
你是一个专业的银行虚拟柜员，你的职责是为客户提供准确、安全、合规的银行服务。

# 历史对话摘要:
{memory}

# 银行服务规范
1. 严格遵守银行相关法规和合规要求
2. 对于涉及资金的操作，必须进行多重身份验证
3. 不得透露客户隐私信息和银行内部信息
4. 对于复杂业务，应引导客户到人工柜台办理
5. 回答应准确、专业、礼貌

# 可执行的银行操作
1. 账户余额查询
2. 最近交易记录查询
3. 理财产品推荐
4. 贷款产品介绍
5. 信用卡申请引导
6. 银行业务咨询

# 回复要求
1. 回答应专业、准确、简洁
2. 如需调用工具，先不要回答，调用工具后再回答
3. 输出格式```json\n{"function_name":"", "args":{}}```
4. 涉及资金操作时，必须提醒客户注意安全
"""

class VirtualTellerRobot(ABC):
    """
    虚拟柜员机器人，专为银行场景设计
    """
    def __init__(self, config_file):
        config = read_config(config_file)
        self.audio_queue = queue.Queue()

        # 初始化基础语音处理模块
        self.recorder = recorder.create_instance(
            config["selected_module"]["Recorder"],
            config["Recorder"][config["selected_module"]["Recorder"]]
        )

        self.vad = vad.create_instance(
            config["selected_module"]["VAD"],
            config["VAD"][config["selected_module"]["VAD"]]
        )

        self.asr = asr.create_instance(
            config["selected_module"]["ASR"],
            config["ASR"][config["selected_module"]["ASR"]]
        )

        self.llm = llm.create_instance(
            config["selected_module"]["LLM"],
            config["LLM"][config["selected_module"]["LLM"]]
        )

        self.tts = tts.create_instance(
            config["selected_module"]["TTS"],
            config["TTS"][config["selected_module"]["TTS"]]
        )

        self.player = player.create_instance(
            config["selected_module"]["Player"],
            config["Player"][config["selected_module"]["Player"]]
        )

        # 初始化银行专用模块
        self.bank_operations = BankOperations()
        self.compliance_checker = ComplianceChecker()
        
        # 初始化记忆和对话管理
        self.memory = memory.Memory(config.get("Memory"))
        self.prompt = banking_sys_prompt.replace("{memory}", self.memory.get_memory()).strip()

        self.vad_queue = queue.Queue()
        self.dialogue = Dialogue(config["Memory"]["dialogue_history_path"])
        self.dialogue.put(Message(role="system", content=self.prompt))

        self.vad_start = True
        # 保证tts是顺序的
        self.tts_queue = queue.Queue()
        # 初始化线程池
        self.executor = ThreadPoolExecutor(max_workers=10)

        # 打断相关配置
        self.INTERRUPT = config["interrupt"]
        self.silence_time_ms = int((1000 / 1000) * (16000 / 512))  # ms

        # 线程锁
        self.chat_lock = False

        # 事件用于控制程序退出
        self.stop_event = threading.Event()

        self.callback = None

        self.speech = []

        # 初始化单例
        rag.Rag(config["Rag"])  # 第一次初始化

        self.task_queue = queue.Queue()
        self.task_manager = TaskManager(config.get("TaskManager"), self.task_queue)
        self.start_task_mode = config.get("StartTaskMode")

    def listen_dialogue(self, callback):
        self.callback = callback

    def shutdown(self):
        """关闭所有资源，确保程序安全退出"""
        logger.info("Shutting down Virtual Teller Robot...")
        self.stop_event.set()
        self.executor.shutdown(wait=True)
        self.recorder.stop_recording()
        self.player.shutdown()
        logger.info("Virtual Teller Robot shutdown complete.")

    def chat_tool(self, query):
        """处理银行相关工具调用"""
        # 检查合规性
        if not self.compliance_checker.check_query_compliance(query):
            logger.warning(f"Query failed compliance check: {query}")
            return []
            
        # 打印逐步生成的响应内容
        start = 0
        try:
            start_time = time.time()  # 记录开始时间
            llm_responses = self.llm.response_call(self.dialogue.get_llm_dialogue(), functions_call=self.task_manager.get_functions())
        except Exception as e:
            logger.error(f"LLM processing error {query}: {e}")
            return []

        tool_call_flag = False
        response_message = []
        # tool call 参数
        function_name = None
        function_id = None
        function_arguments = ""
        content_arguments = ""
        for chunk in llm_responses:
            content, tools_call = chunk
            if content is not None and len(content)>0:
                if len(response_message)<=0 and content=="```":
                    tool_call_flag = True
            if tools_call is not None:
                tool_call_flag = True
                if tools_call[0].id is not None:
                    function_id = tools_call[0].id
                if tools_call[0].function.name is not None:
                    function_name = tools_call[0].function.name
                if tools_call[0].function.arguments is not None:
                    function_arguments += tools_call[0].function.arguments
            if content is not None and len(content) > 0:
                if tool_call_flag:
                    content_arguments+=content
                else:
                    response_message.append(content)
                    end_time = time.time()  # 记录结束时间
                    logger.debug(f"LLM response time: {end_time - start_time} seconds, tokens={content}")
                    if is_segment(response_message):
                        segment_text = "".join(response_message[start:])
                        # 为了保证语音的连贯，至少2个字才转tts
                        if len(segment_text) <= max(2, start):
                            continue
                        future = self.executor.submit(self.speak_and_play, segment_text)
                        self.tts_queue.put(future)
                        start = len(response_message)

        if not tool_call_flag:
            if start < len(response_message):
                segment_text = "".join(response_message[start:])
                future = self.executor.submit(self.speak_and_play, segment_text)
                self.tts_queue.put(future)
        else:
            # 处理函数调用
            if function_id is None:
                a = extract_json_from_string(content_arguments)
                if a is not None:
                    content_arguments_json = json.loads(a)
                    function_name = content_arguments_json["function_name"]
                    function_arguments = json.dumps(content_arguments_json["args"], ensure_ascii=False)
                    function_id = str(uuid.uuid4().hex)
                else:
                    return []
                function_arguments = json.loads(function_arguments)
            logger.info(f"function_name={function_name}, function_id={function_id}, function_arguments={function_arguments}")
            
            # 银行操作前进行额外的安全检查
            if not self.bank_operations.is_safe_operation(function_name, function_arguments):
                error_msg = "该操作存在安全风险，无法执行。"
                logger.warning(f"Unsafe operation blocked: {function_name}")
                future = self.executor.submit(self.speak_and_play, error_msg)
                self.tts_queue.put(future)
                return []
            
            # 调用工具
            result = self.task_manager.tool_call(function_name, function_arguments)
            if result.action == Action.NOTFOUND:
                logger.error(f"Function not found: {function_name}")
                return []
            elif result.action == Action.NONE:
                return []
            elif result.action == Action.RESPONSE:
                # 检查响应是否符合合规要求
                if not self.compliance_checker.check_response_compliance(result.result):
                    logger.warning("Response failed compliance check")
                    result.result = "出于合规要求，我无法提供该信息。"
                
                future = self.executor.submit(self.speak_and_play, result.result)
                self.tts_queue.put(future)
                return [{"role": "assistant", "content": result.result}]
            elif result.action == Action.ASYNC:
                self.task_queue.put(result.future)
                return []

    def speak_and_play(self, text):
        """将文本转换为语音并播放"""
        try:
            # 检查响应是否符合合规要求
            if not self.compliance_checker.check_response_compliance(text):
                logger.warning("Response failed compliance check")
                text = "出于合规要求，我无法提供该信息。"
                
            tts_file = self.tts.to_tts(text)
            if tts_file:
                self.player.play(tts_file)
                logger.info(f"Playing TTS: {text}")
            return tts_file
        except Exception as e:
            logger.error(f"Error in speak_and_play: {e}")
            return None

    def run(self):
        """运行虚拟柜员机器人"""
        logger.info("Virtual Teller Robot started")
        try:
            while not self.stop_event.is_set():
                # 这里可以添加虚拟柜员的特定逻辑
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in Virtual Teller Robot: {e}")
        finally:
            self.shutdown()