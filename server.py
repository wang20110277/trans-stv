import threading
import time
import os
from gtts import gTTS

from fastapi import FastAPI, WebSocket, Query, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, List

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('server.log')  # 文件输出
    ]
)

logger = logging.getLogger(__name__)

# 存储对话历史
dialogue: List[Dict] = []
# 存储活跃连接
active_connections: Dict[str, WebSocket] = {}
# 存储用户对话历史
user_dialogues: Dict[str, List[Dict]] = {}
# 存储用户连接时间，用于清理超时连接
user_last_active: Dict[str, float] = {}

# 语音文件存储目录
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# 清理超时连接的任务
async def cleanup_inactive_connections():
    while True:
        try:
            current_time = time.time()
            inactive_users = []
            for user_id, last_active in user_last_active.items():
                # 超过10分钟没有活动的连接将被清理
                if current_time - last_active > 600:
                    inactive_users.append(user_id)
            
            for user_id in inactive_users:
                if user_id in active_connections:
                    try:
                        await active_connections[user_id].close()
                    except:
                        pass
                    del active_connections[user_id]
                if user_id in user_last_active:
                    del user_last_active[user_id]
                logger.info(f"清理超时连接: {user_id}")
        except Exception as e:
            logger.error(f"清理超时连接时出错: {e}")
        
        # 每30秒检查一次
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("服务器启动")
    # 启动清理任务
    cleanup_task = asyncio.create_task(cleanup_inactive_connections())
    yield
    # 关闭时执行
    cleanup_task.cancel()
    logger.info("服务器关闭")

app = FastAPI(lifespan=lifespan)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（必须在路由定义之前）
if os.path.exists("templates"):
    app.mount("/static", StaticFiles(directory="templates"), name="static")

# 挂载assets目录以提供图片等静态资源
assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """提供主页面"""
    if os.path.exists("templates/index.html"):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>阿雅实时对话服务器</h1><p>页面文件未找到</p>"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Query(...)):
    """处理WebSocket连接"""
    await websocket.accept()
    active_connections[user_id] = websocket
    user_last_active[user_id] = time.time()
    logger.info(f"用户 {user_id} 已连接")
    
    # 初始化用户对话历史
    if user_id not in user_dialogues:
        user_dialogues[user_id] = []
    
    try:
        # 发送当前对话历史给新连接的用户
        await websocket.send_json({"type": "update_dialogue", "data": user_dialogues[user_id]})
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            user_last_active[user_id] = time.time()
            logger.info(f"收到来自用户 {user_id} 的消息: {data}")
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")
                
                if message_type == "message":
                    # 处理普通消息
                    message = {
                        'role': message_data.get('role', 'user'),
                        'content': message_data.get('content', ''),
                        'start_time': "",
                        'end_time': "",
                        'audio_file': "",
                        'tts_file': "",
                        'vad_status': ""
                    }
                    
                    # 添加到全局对话和用户对话历史
                    dialogue.append(message)
                    user_dialogues[user_id].append(message)
                    
                    # 广播给所有连接的用户
                    await broadcast_message({"type": "update_dialogue", "data": dialogue})
                    
                elif message_type == "ping":
                    # 心跳检测
                    await websocket.send_json({"type": "pong"})
                    
                else:
                    logger.warning(f"未知消息类型: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"JSON解析错误: {data}")
                
    except WebSocketDisconnect:
        logger.info(f"用户 {user_id} 断开连接")
    except Exception as e:
        logger.error(f"处理WebSocket消息时出错: {e}")
    finally:
        # 清理连接
        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in user_last_active:
            del user_last_active[user_id]

async def broadcast_message(message: dict):
    """广播消息给所有活跃连接"""
    disconnected_users = []
    for user_id, websocket in active_connections.items():
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            disconnected_users.append(user_id)
        except Exception as e:
            logger.error(f"向用户 {user_id} 发送消息时出错: {e}")
            disconnected_users.append(user_id)
    
    # 清理断开的连接
    for user_id in disconnected_users:
        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in user_last_active:
            del user_last_active[user_id]

@app.post("/add_message")
async def add_message(message_data: dict):
    """添加消息接口"""
    try:
        message = {
            'role': message_data.get('role'),
            'content': message_data.get('content'),
            'start_time': "",
            'end_time': "",
            'audio_file': "",
            'tts_file': "",
            'vad_status': ""
        }
        dialogue.append(message)
        
        # 广播更新
        await broadcast_message({"type": "update_dialogue", "data": dialogue})
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"添加消息时出错: {e}")
        return {"status": "error", "message": str(e)}


async def generate_tts(text: str) -> str:
    """将文本转换为语音文件"""
    try:
        tts = gTTS(text=text, lang='zh-cn')
        filename = f"{int(time.time())}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        tts.save(filepath)
        return filename  # 返回文件名
    except Exception as e:
        logger.error(f"TTS生成失败: {e}")
        return ""

@app.get("/dialogue")
async def get_dialogue():
    """获取对话历史"""
    return dialogue

@app.delete("/dialogue")
async def clear_dialogue():
    """清空对话历史"""
    dialogue.clear()
    user_dialogues.clear()
    # 通知所有客户端清空对话
    await broadcast_message({"type": "update_dialogue", "data": []})
    return {"status": "success"}

if __name__ == '__main__':
    uvicorn.run(

        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境中关闭自动重载
        log_level="info"
    )