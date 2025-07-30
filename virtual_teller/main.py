#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
银行虚拟柜员主程序入口
"""

import argparse
import logging
import threading
import yaml
import json
import requests

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('tmp/virtual_teller.log')  # 文件输出
    ]
)

from virtual_teller.core.teller_robot import VirtualTellerRobot

# 获取根 logger
logger = logging.getLogger(__name__)

def load_config(config_path):
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

# 全局变量
teller_robot = None

def push2web(payload):
    """推送消息到Web端"""
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
        logger.error(f"推送消息到Web端出错：{payload}{e}")

def process_user_message(message_data):
    """处理用户发送的消息"""
    global teller_robot
    try:
        # 获取消息内容
        content = message_data.get('content', '')
        if not content:
            logger.warning("收到空消息")
            return
            
        logger.info(f"收到用户消息: {content}")
        
        # 如果有机器人实例，使用机器人处理消息
        if teller_robot:
            # 在新线程中处理消息，避免阻塞
            thread = threading.Thread(target=teller_robot.chat, args=(content,))
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        logger.error(f"处理用户消息时出错: {e}")

def main():
    """主函数"""
    global teller_robot
    
    parser = argparse.ArgumentParser(description="银行虚拟柜员系统")

    # 添加参数
    parser.add_argument('--config_path', type=str, help="配置文件路径", 
                       default="virtual_teller/config/teller_config.yaml")

    # 解析参数
    args = parser.parse_args()
    config_path = args.config_path

    # 加载配置
    config = load_config(config_path)
    
    # 创建虚拟柜员机器人实例并运行
    teller_robot = VirtualTellerRobot(config_path)
    teller_robot.listen_dialogue(push2web)
    
    # 启动机器人（在单独的线程中）
    robot_thread = threading.Thread(target=teller_robot.run)
    robot_thread.daemon = True
    robot_thread.start()
    
    logger.info("银行虚拟柜员系统已启动")
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
        if teller_robot:
            teller_robot.shutdown()
        logger.info("程序退出")

if __name__ == "__main__":
    main()