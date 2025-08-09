import json
import subprocess
import logging
from plugins.registry import register_function, ToolType, Action, ActionResponse

logger = logging.getLogger(__name__)

# 注册MCP调用函数
@register_function("mcp_call", ToolType.WAIT)
def mcp_call(server_name: str, command: str = None, args: list = None) -> ActionResponse:
    """
    调用MCP服务器执行命令
    
    Args:
        server_name (str): MCP服务器名称
        command (str, optional): 要执行的命令
        args (list, optional): 命令参数列表
        
    Returns:
        ActionResponse: 包含执行结果的响应对象
    """
    try:
        # 读取MCP服务器配置
        mcp_config = _load_mcp_config()
        
        # 检查服务器是否存在
        if server_name not in mcp_config.get("mcpServers", {}):
            return ActionResponse(
                action=Action.RESPONSE,
                result=None,
                response=f"MCP服务器 '{server_name}' 未找到"
            )
        
        # 获取服务器配置
        server_config = mcp_config["mcpServers"][server_name]
        cmd = server_config["command"]
        
        # 构建命令参数
        cmd_args = server_config.get("args", [])
        if command:
            cmd_args.append(command)
        if args:
            cmd_args.extend(args)
        
        # 执行命令
        logger.info(f"执行MCP命令: {cmd} {' '.join(cmd_args)}")
        result = subprocess.run(
            [cmd] + cmd_args,
            capture_output=True,
            text=True,
            timeout=30  # 设置30秒超时
        )
        
        # 检查执行结果
        if result.returncode == 0:
            output = result.stdout.strip()
            return ActionResponse(
                action=Action.RESPONSE,
                result=output,
                response=output
            )
        else:
            error_msg = result.stderr.strip()
            logger.error(f"MCP命令执行失败: {error_msg}")
            return ActionResponse(
                action=Action.RESPONSE,
                result=None,
                response=f"执行MCP命令时出错: {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        logger.error("MCP命令执行超时")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response="MCP命令执行超时"
        )
    except Exception as e:
        logger.error(f"MCP调用出错: {str(e)}")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"MCP调用出错: {str(e)}"
        )

def _load_mcp_config():
    """
    加载MCP配置
    
    Returns:
        dict: MCP配置字典
    """
    # 默认配置
    default_config = {
        "mcpServers": {}
    }
    
    # 尝试从文件加载配置
    try:
        with open("mcp_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.warning("未找到mcp_config.json文件，使用默认配置")
        return default_config
    except json.JSONDecodeError as e:
        logger.error(f"解析mcp_config.json文件出错: {str(e)}")
        return default_config