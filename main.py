import argparse
import json
import logging
import requests
import threading
import time
import yaml

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('tmp/trans-stv.log')  # 文件输出
    ]
)

from src import robot
from src.tts import create_instance

# 获取根 logger
logger = logging.getLogger(__name__)

def load_config(config_path):
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

# 全局变量
robot_instance = None
tts_instance = None

def initialize_tts(config):
    """初始化TTS引擎"""
    global tts_instance
    try:
        tts_config = config.get('TTS', {})
        selected_tts = config.get('selected_module', {}).get('TTS', 'MacTTS')
        tts_params = tts_config.get(selected_tts, {})
        tts_instance = create_instance(selected_tts, tts_params)
        logger.info(f"TTS引擎初始化成功: {selected_tts}")
    except Exception as e:
        logger.error(f"TTS引擎初始化失败: {e}")
        tts_instance = None

def text_to_speech_and_play(text):
    """将文本转换为语音并播放"""
    global tts_instance, robot_instance
    if not tts_instance:
        logger.error("TTS引擎未初始化")
        return None
    
    try:
        # 将文本转换为语音文件
        tts_file = tts_instance.to_tts(text)
        if not tts_file:
            logger.error("文本转语音失败")
            return None
            
        # 使用机器人播放语音
        if robot_instance and robot_instance.player:
            robot_instance.player.play(tts_file)
            logger.info(f"语音播放完成: {text}")
        else:
            logger.warning("机器人播放器未初始化")
            
        return tts_file
    except Exception as e:
        logger.error(f"文本转语音并播放时出错: {e}")
        return None

def push2web(payload):
    try:
        data = json.dumps(payload, ensure_ascii=False)
        # 更新URL为新的FastAPI服务器地址
        url = "http://127.0.0.1:8000/add_message"
        headers = {
          'Content-Type': 'application/json; charset=utf-8'
        }
        response = requests.request("POST", url, headers=headers, data=data.encode('utf-8'))
        logger.info(response.text)
    except Exception as e:
        logger.error(f"callback error：{payload}{e}")

def process_user_message(message_data):
    """处理用户发送的消息"""
    global robot_instance
    try:
        # 获取消息内容
        content = message_data.get('content', '')
        if not content:
            logger.warning("收到空消息")
            return
            
        logger.info(f"收到用户消息: {content}")
        
        # 如果有机器人实例，使用机器人处理消息
        if robot_instance:
            # 在新线程中处理消息，避免阻塞
            thread = threading.Thread(target=robot_instance.chat, args=(content,))
            thread.daemon = True
            thread.start()
        else:
            # 直接使用TTS播放文本
            text_to_speech_and_play(content)
            
    except Exception as e:
        logger.error(f"处理用户消息时出错: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script.")

    # Add arguments
    parser.add_argument('--config_path', type=str, help="配置文件", default="config/config.yaml")

    # Parse arguments
    args = parser.parse_args()
    config_path = args.config_path

    # 加载配置
    config = load_config(config_path)
    
    # 初始化TTS引擎
    initialize_tts(config)
    
    # 创建 Robot 实例并运行
    robot_instance = robot.Robot(config_path)
    robot_instance.listen_dialogue(push2web)
    
    # 启动机器人（在单独的线程中）
    robot_thread = threading.Thread(target=robot_instance.run)
    robot_thread.daemon = True
    robot_thread.start()
    
    logger.info("阿雅语音助手已启动")
    logger.info("支持语音输入和文本输入，输入'text:内容'可以直接将文本转为语音")
    logger.info("输入'quit'退出程序")
    
    try:
        while True:
            # 从控制台读取输入
            user_input = input()
            
            # 检查是否是特殊命令
            if user_input.lower() == 'quit':
                logger.info("正在退出程序...")
                break
                
            # 检查是否是文本输入命令
            if user_input.startswith('text:'):
                content = user_input[5:].strip()  # 移除'text:'前缀
                if content:
                    # 创建消息数据结构
                    message_data = {
                        'role': 'user',
                        'content': content
                    }
                    # 处理消息
                    process_user_message(message_data)
            else:
                # 直接处理普通文本
                message_data = {
                    'role': 'user',
                    'content': user_input
                }
                process_user_message(message_data)
                
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"主循环出错: {e}")
    finally:
        logger.info("程序退出")