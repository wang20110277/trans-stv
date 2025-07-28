# 阿雅语音对话助手需求文档
## 1. 项目概述
阿雅（trans-stv）是一个开源语音对话助手，通过整合语音识别(ASR)、语音活动检测(VAD)、大语言模型(LLM)和语音合成(TTS)技术，实现类GPT-4o的语音对话体验，端到端时延800ms。项目设计目标是在无需GPU的边缘设备和低资源环境下提供高质量交互。

## 2. 核心功能需求
### 2.1 基础对话功能
- 语音输入输出：支持麦克风录音输入和扬声器语音输出
- 实时语音处理：通过VAD技术检测有效语音片段，过滤背景噪音
- 语音转文本：使用FunASR模型将语音转换为文本
- 智能回复生成：通过LLM处理文本输入并生成自然语言回复
- 文本转语音：支持多种TTS引擎(MacTTS、EdgeTTS、ChatTTS等)将文本转换为自然语音
### 2.2 高级功能
- 记忆功能 ：通过Memory模块记录用户偏好和历史对话，提供个性化交互
- 工具调用 ：支持天气查询、雅思口语练习、定时任务、应用打开等工具集成
- 任务管理 ：创建、跟踪和管理用户任务，设置提醒和进度更新
- 本地文档搜索 ：基于RAG技术实现本地文档检索和问答
- 数字人功能 ：通过SadTalker将语音驱动图片人脸，实现数字人说话效果
## 3. 非功能需求
### 3.1 性能要求
- 端到端延迟：≤800ms
- CPU占用：在i5处理器上优化至合理水平
- 内存占用：控制在可接受范围内
- 响应准确率：达到行业领先水平
### 3.2 兼容性要求
- 操作系统：支持macOS
- Python版本：3.8及以上
- 硬件环境：无需GPU，可在树莓派4及以上设备运行
### 3.3 可靠性要求
- 模块化设计：各组件(VAD、ASR、LLM、TTS)独立，支持单独替换升级
- 错误处理：完善的日志记录和异常处理机制
- 稳定性：持续对话无崩溃，平均无故障时间长
## 4. 系统架构
### 4.1 技术架构
项目采用模块化设计，主要包含以下组件：

- Recorder ：音频录制模块，支持PyAudio
- VAD ：语音活动检测，使用silero-vad
- ASR ：语音识别，使用FunASR
- LLM ：大语言模型，支持OllamaLLM等多种模型
- TTS ：语音合成，支持多种TTS引擎
- Player ：音频播放模块
- Memory ：对话记忆管理
- RAG ：本地文档检索系统
- TaskManager ：任务管理和工具调用
### 4.2 核心流程
1. 1.
   用户语音输入 → 2. VAD检测有效语音 → 3. ASR转文本 → 4. LLM生成回复 → 5. TTS转语音 → 6. 播放回复
## 5. 模块详细设计
### 5.1 配置参数
主要配置文件为config/config.yaml，包含：

- 模块选择：指定使用的Recorder、ASR、VAD、LLM、TTS等实现
- 模型参数：采样率、阈值、模型路径等
- 路径配置：临时文件目录、模型目录等
- 功能开关：是否开启工具调用、打断功能等
### 5.2 工具调用接口
支持以下工具函数（定义于plugins/function_calls_config.json）：

函数名 描述 参数 get_weather 获取天气信息 city: 城市路径(如zhejiang/hangzhou) ielts_speaking_practice 雅思口语练习 topic: 练习主题 schedule_task 创建定时任务 time: 时间(HH:mm), content: 任务内容 open_application 打开应用 application_name: 应用名称 web_search 网络搜索 query: 搜索关键词 search_local_documents 本地文档搜索 keyword: 查询关键词

## 6. 安装与部署
### 6.1 环境依赖
- Python 3.8+
- 依赖库：详见requirements.txt，主要包括chattts、edge_tts、funasr、silero_vad等
- 系统工具：ffmpeg
### 6.2 部署步骤
1. 1.
   克隆仓库并进入目录
2. 2.
   安装依赖：pip install -r requirements.txt
3. 3.
   配置环境变量和模型路径
4. 4.
   启动服务：python main.py
## 7. 未来扩展规划
- 支持语音唤醒
- 强化Web搜索功能
- 支持WebRTC实现远程访问
- 扩展更多第三方服务集成
## 8. 技术选型
功能 技术选型 语音活动检测 silero-vad 语音识别 FunASR(SenseVoiceSmall模型) 大语言模型 OllamaLLM(qwen2.5:14b等) 语音合成 MacTTS/EdgeTTS/ChatTTS等 数字人 SadTalker 记忆管理 自定义Memory模块 本地检索 RAG(LangChain+Chroma)