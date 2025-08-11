# 阿雅

**阿雅** 是一个语音对话助手，旨在通过语音与用户进行自然的对话。该项目结合了语音识别 (ASR)、语音活动检测 (VAD)、大语言模型 (LLM) 和语音合成 (TTS) 技术，这是一个类似GPT-4o的语音对话机器人，通过ASR+LLM+TTS实现，提供高质量的语音对话体验，端到端时延800ms。阿雅旨在无需GPU的情况下，实现类GPT-4o的对话效果，适用于各种边缘设备和低资源环境。

## 项目特点

- **高效开源模型**：阿雅使用了多个开源模型，确保高效、可靠的语音对话体验。
- **无需GPU**：通过优化，可本地部署，仍能提供类GPT-4的性能表现。
- **模块化设计**：VAD、ASR、LLM和TTS模块相互独立，可以根据需求进行替换和升级。
- **支持记忆功能**: 具备持续学习能力，能够记忆用户的偏好与历史对话，提供个性化的互动体验。
- **支持工具调用**: 灵活集成外部工具，用户可通过语音直接请求信息或执行操作，提升助手的实用性。
- **支持任务管理**: 高效管理用户任务，能够跟踪进度、设置提醒，并提供动态更新，确保用户不错过任何重要事项。


## 项目简介

阿雅通过以下技术组件实现语音对话功能：
- **VAD**: 使用 [silero-vad](https://github.com/snakers4/silero-vad) 进行语音活动检测，以确保只处理有效的语音片段。
- **ASR**: 使用 [FunASR](https://github.com/modelscope/FunASR) 进行自动语音识别，将用户的语音转换为文本。
- **LLM**: 使用 [deepseek](https://github.com/deepseek-ai/DeepSeek-LLM) 作为大语言模型来处理用户输入并生成响应，极具性价比。
- **TTS**: 使用 [edge-tts](https://github.com/rany2/edge-tts) [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) [ChatTTS](https://github.com/2noise/ChatTTS) MacOS say进行文本到语音的转换，将生成的文本响应转换为自然流畅的语音。
- **THG**: 使用 [SadTalker](https://github.com/OpenTalker/SadTalker) [MuseTalk](https://github.com/TMElyralab/MuseTalk/tree/main) 语音驱动人脸生成

## 框架说明

![阿雅流程图](assets/images/data_flow.svg)

Robot 负责高效的任务管理与记忆管理，能够智能地处理用户的打断请求，同时实现各个模块之间的无缝协调与连接，以确保流畅的交互体验。

| 播放器状态 | 是否说话 | 说明 |
|----------|----------|----------|
| 播放中 | 未说话 | 正常 |
| 播放中 | 说话 | 打断场景 |
| 未播放| 未说话 | 正常 |
| 未播放| 说话 | VAD判断，ASR识别 |
documents - RAG文档管理
功能：实现RAG（Retrieval-Augmented Generation）的文档存储和检索-bge-small-zh
组织方式：按目录放置不同产品的文档
作用：为大语言模型提供外部知识库，增强回答的准确性和相关性

plugins - MCP工具集成
功能：实现Model Context Protocol (MCP)工具集成
配置文件：mcp_config.json 中定义可用的MCP服务器
使用方式：通过 mcp_call 函数调用各种MCP工具和服务
示例：12306火车票查询等外部服务集成

third_party - Agent实现
功能：集成不同的agent实现，用于操作本地生成文档、检索等
示例提及：OpenManus 的依赖安装 (pip install -r third_party/OpenManus/requirements.txt)

## 功能特性

- **语音输入**：通过 FunASR 进行准确的语音识别。
- **语音活动检测**：使用 silero-vad 过滤无效音频，提升识别效率。
- **智能对话生成**：依靠 deepseek 提供的强大语言理解能力生成自然的文本回复，极具性价比。
- **语音输出**：通过 edge-tts Kokoro-82M 将文本转为语音，为用户提供逼真的听觉反馈。
- **数字人**：通过 SadTalker 将语音转为数字人，为用户提供逼真的视听反馈。
- **支持打断**：灵活配置打断策略，能够识别关键字和语音打断，确保用户在对话中的即时反馈与控制，提高交互流畅度。
- **支持记忆功能**: 具备持续学习能力，能够记忆用户的偏好与历史对话，提供个性化的互动体验。
- **支持工具调用**: 灵活集成外部工具，用户可通过语音直接请求信息或执行操作，提升助手的实用性。
- **支持任务管理**: 高效管理用户任务，能够跟踪进度、设置提醒，并提供动态更新，确保用户不错过任何重要事项。

## 项目优势

- **高质量语音对话**：整合了优秀的ASR、LLM和TTS技术，确保语音对话的流畅性和准确性。
- **轻量化设计**：无需高性能硬件即可运行，适用于资源受限的环境。
- **完全开源**：阿雅完全开源，鼓励二次开发。

## 安装与运行

### 依赖环境

请确保你的开发环境中安装了以下工具和库：

- 安装miniconda
- Python 3.8 或更高版本
- `pip` 包管理器
- FunASR、silero-vad、deepseek、edge-tts、Kokoro-82M 、SadTalker 所需的依赖库

### 安装步骤

1. 克隆项目仓库：

    ```bash
    cd trans-stv
    ```

2. 安装所需依赖：

    ```bash
    pip install -r requirements.txt
    pip install -r third_party/OpenManus/requirements.txt 
    conda install ffmpeg
    ```

3. 配置环境变量：

     - 打开config/config.yaml 配置ASR LLM等相关配置
     - 下载SenseVoiceSmall到目录models/SenseVoiceSmall [SenseVoiceSmall下载地址](https://huggingface.co/FunAudioLLM/SenseVoiceSmall/tree/main)
     - 下载bge-small-zh到目录models/bge-small-zh [bge-small-zh下载地址]
     - 去deepseek官网，获取配置api_key，[deepseek获取api_key](https://platform.deepseek.com/api_keys)，当然也可以配置openai、qwen、gemini、01yi等其他模型

4. 运行项目：
    ```bash
    python main.py
    ```

## 使用说明

1. 启动应用后，系统会等待语音输入。
2. 通过 FunASR 将用户语音转为文本。
3. silero-vad 进行语音活动检测，确保只处理有效语音。
4. deepseek 处理文本输入，并生成智能回复。
5. edge-tts, Kokoro-82M, ChatTTS, MacOs say 将生成的文本转换为语音，并播放给用户。
6. SadTalker 将语音驱动图片人脸，实现数字人说话。

## 支持的工具
## 功能

- **动态功能调用**：通过定义函数接口，实现动态调用功能。
- **灵活配置**：支持多种功能配置方式。

## 配置

1. **创建配置文件**：在项目根目录下创建一个名为 `function_calls_config.json` 的配置文件。该文件将用于定义你的 function call 相关配置。
    ```json
   {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取某个地点的天气，用户应先提供一个位置，比如用户说杭州天气，参数为：zhejiang/hangzhou，比如用户说北京天气怎么样，参数为：beijing/beijing",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市，zhejiang/hangzhou"
                    }
                },
                "required": [
                    "city"
                ]
            }
        }
    }
    ```
   
2. **实现函数逻辑**：在functions文件夹下，实现你的工具逻辑

```python
import requests
from bs4 import BeautifulSoup

from plugins.registry import register_function
from plugins.registry import ActionResponse, Action

@register_function('get_weather')
def get_weather(city: str):
    """
    "获取某个地点的天气，用户应先提供一个位置，\n比如用户说杭州天气，参数为：zhejiang/hangzhou，\n\n比如用户说北京天气怎么样，参数为：beijing/beijing",
    city : 城市，zhejiang/hangzhou
    """
    url = "https://tianqi.moji.com/weather/china/"+city
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code!=200:
        return ActionResponse(Action.REQLLM, None, "请求失败")
    soup = BeautifulSoup(response.text, "html.parser")
    weather = soup.find('meta', attrs={'name':'description'})["content"]
    weather = weather.replace("墨迹天气", "")
    return ActionResponse(Action.REQLLM, None, weather)

if __name__ == "__main__":
    print(get_weather("zhejiang/hangzhou"))
 
```
3. 当前支持的工具有：

| 函数名                | 描述                                          | 功能                                                       | 示例                                                         |
|-----------------------|-----------------------------------------------|------------------------------------------------------------|--------------------------------------------------------------|
| `get_weather`         | 获取某个地点的天气信息                        | 提供地点名称后，返回该地点的天气情况                       | 用户说：“杭州天气怎么样？” → `zhejiang/hangzhou`             |
| `ielts_speaking_practice` | IELTS（雅思）口语练习                     | 生成雅思口语练习题目和对话，帮助用户进行雅思口语练习       | -                                                            |
| `get_day_of_week`     | 获取当前的星期几或日期                        | 当用户询问当前时间、日期或者星期几时，返回相应的信息       | 用户说：“今天星期几？” → 返回当前的星期几                    |
| `schedule_task`       | 创建一个定时任务                              | 用户可以指定任务的执行时间和内容，定时提醒用户             | 用户说：“每天早上8点提醒我喝水。” → `time: '08:00', content: '提醒我喝水'` |
| `open_application`    | 在 Mac 电脑上打开指定的应用程序                | 用户可以指定应用程序的名称，脚本将在 Mac 上启动相应的应用 | 用户说：“打开Safari。” → `application_name: 'Safari'`        |
| `web_search`          | 在网上搜索指定的关键词                        | 根据用户提供的搜索内容，返回相应的搜索结果                 | 用户说：“搜索最新的科技新闻。” → `query: '最新的科技新闻'`    |

## MCP集成

本项目支持Model Context Protocol (MCP)集成，可以方便地调用各种MCP服务器提供的功能。

### 配置MCP服务器

在项目根目录的 `mcp_config.json` 文件中配置可用的MCP服务器：

```json
{
  "mcpServers": {
    "12306-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "12306-mcp"
      ]
    }
  }
}
```
## Roadmap
- [x] 基本语音对话功能
- [x] 支持插件调用
- [x] 任务管理
- [x] Rag & Agent
- [x] Memory
- [ ] 支持语音唤醒
- [ ] 强化WebSearch
- [ ] 支持WebRTC
未来，阿雅将升华为一款类JARVIS个人助手，仿佛一位贴心的智囊，具备无与伦比的记忆力与前瞻性的任务管理能力。依托于尖端的RAG、MCP、Agent技术，它将精确掌控您的事务与知识，化繁为简。只需轻声一语，例如"帮我查找最近新闻"或"总结大模型的最新进展"，阿雅便会迅速响应，智能分析，实时跟踪，并将成果优雅地呈现给您。想象一下，您拥有的不仅是一名助手，而是一个深谙您需求的智慧伙伴，伴您在未来的每个重要瞬间，助您洞察万象，决胜千里。