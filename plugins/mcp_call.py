import json
import subprocess
import logging
import os
import time
from typing import Optional, Dict, Any
from plugins.registry import register_function, ToolType, Action, ActionResponse

logger = logging.getLogger(__name__)

# MCP配置文件路径，可以通过环境变量覆盖
MCP_CONFIG_PATH = os.environ.get("MCP_CONFIG_PATH", "mcp_config.json")

# 注册MCP调用函数
@register_function("mcp_call", ToolType.WAIT)
def mcp_call(
    server_name: str,
    command: Optional[str] = None,
    args: Optional[list] = None,
    timeout: int = 30,
    check_status: bool = True
) -> ActionResponse:
    """
    调用MCP服务器执行命令
    
    Args:
        server_name (str): MCP服务器名称
        command (str, optional): 要执行的命令
        args (list, optional): 命令参数列表
        timeout (int, optional): 命令执行超时时间(秒)，默认30秒
        check_status (bool, optional): 是否检查服务器状态，默认True
    
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
        
        # 检查服务器状态（如果需要）
        if check_status:
            status_result = _check_server_status(server_name, server_config)
            if not status_result.success:
                return ActionResponse(
                    action=Action.RESPONSE,
                    result=None,
                    response=f"MCP服务器 '{server_name}' 状态检查失败: {status_result.message}"
                )
        
        # 执行命令
        logger.info(f"执行MCP命令: {cmd} {' '.join(cmd_args)}")
        start_time = time.time()
        result = subprocess.run(
            [cmd] + cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        execution_time = time.time() - start_time
        logger.info(f"MCP命令执行完成，耗时: {execution_time:.2f}秒")
        
        # 检查执行结果
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.debug(f"MCP命令执行成功，输出: {output}")
            return ActionResponse(
                action=Action.RESPONSE,
                result=output,
                response=output
            )
        else:
            error_msg = result.stderr.strip()
            logger.error(f"MCP命令执行失败 (返回码: {result.returncode}): {error_msg}")
            return ActionResponse(
                action=Action.RESPONSE,
                result=None,
                response=f"执行MCP命令时出错 (返回码: {result.returncode}): {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        logger.error(f"MCP命令执行超时 (>{timeout}秒)")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"MCP命令执行超时 (>{timeout}秒)"
        )
    except FileNotFoundError as e:
        logger.error(f"未找到MCP命令: {str(e)}")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"未找到MCP命令: {str(e)}"
        )
    except PermissionError as e:
        logger.error(f"MCP命令执行权限不足: {str(e)}")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"MCP命令执行权限不足: {str(e)}"
        )
    except Exception as e:
        logger.error(f"MCP调用出错: {str(e)}", exc_info=True)
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"MCP调用出错: {str(e)}"
        )

class ServerStatusResult:
    """服务器状态检查结果"""
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message


def _check_server_status(server_name: str, server_config: Dict[str, Any]) -> ServerStatusResult:
    """
    检查MCP服务器状态
    
    Args:
        server_name (str): 服务器名称
        server_config (Dict[str, Any]): 服务器配置
    
    Returns:
        ServerStatusResult: 状态检查结果
    """
    try:
        # 这里实现服务器状态检查逻辑
        # 对于不同类型的服务器，可能需要不同的检查方法
        logger.info(f"检查MCP服务器 '{server_name}' 状态...")
        
        # 示例：发送一个简单的命令来检查服务器是否响应
        cmd = server_config["command"]
        cmd_args = server_config.get("status_args", ["--status"])
        
        result = subprocess.run(
            [cmd] + cmd_args,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"MCP服务器 '{server_name}' 状态正常")
            return ServerStatusResult(True, "服务器状态正常")
        else:
            error_msg = result.stderr.strip() or "未知错误"
            logger.warning(f"MCP服务器 '{server_name}' 状态异常: {error_msg}")
            return ServerStatusResult(False, error_msg)
    
    except Exception as e:
        logger.error(f"检查MCP服务器 '{server_name}' 状态时出错: {str(e)}")
        return ServerStatusResult(False, str(e))

def _load_mcp_config() -> Dict[str, Any]:
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
        config_path = MCP_CONFIG_PATH
        logger.info(f"加载MCP配置文件: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # 验证配置格式
        if not isinstance(config, dict) or "mcpServers" not in config:
            logger.warning("MCP配置格式不正确，使用默认配置")
            return default_config
        
        return config
    except FileNotFoundError:
        logger.warning(f"未找到MCP配置文件: {config_path}，使用默认配置")
        return default_config
    except json.JSONDecodeError as e:
        logger.error(f"解析MCP配置文件出错: {str(e)}")
        return default_config
    except Exception as e:
        logger.error(f"加载MCP配置时出错: {str(e)}")
        return default_config

# 异步版本的MCP调用（非阻塞）
@register_function("mcp_call_async", ToolType.TIME_CONSUMING)
async def mcp_call_async(
    server_name: str,
    command: Optional[str] = None,
    args: Optional[list] = None,
    timeout: int = 30
) -> ActionResponse:
    """
    异步调用MCP服务器执行命令
    
    Args:
        server_name (str): MCP服务器名称
        command (str, optional): 要执行的命令
        args (list, optional): 命令参数列表
        timeout (int, optional): 命令执行超时时间(秒)，默认30秒
    
    Returns:
        ActionResponse: 包含任务ID的响应对象
    """
    try:
        # 在实际实现中，这里应该将任务提交到异步队列
        # 并返回一个任务ID，以便后续查询结果
        task_id = f"mcp_{server_name}_{int(time.time())}"
        logger.info(f"提交异步MCP任务: {task_id}")
        
        # 这里只是模拟异步行为
        # 实际实现需要一个任务队列和工作线程池
        from plugins.task_manager import TaskManager
        TaskManager.submit_task(
            task_id,
            mcp_call,
            server_name=server_name,
            command=command,
            args=args,
            timeout=timeout,
            check_status=True
        )
        
        return ActionResponse(
            action=Action.RESPONSE,
            result={"task_id": task_id},
            response=f"异步MCP任务已提交，任务ID: {task_id}\n可使用 mcp_get_result 命令查询结果"
        )
    except Exception as e:
        logger.error(f"提交异步MCP任务时出错: {str(e)}")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"提交异步MCP任务时出错: {str(e)}"
        )

# 查询异步MCP任务结果
@register_function("mcp_get_result", ToolType.WAIT)
def mcp_get_result(task_id: str) -> ActionResponse:
    """
    查询异步MCP任务结果
    
    Args:
        task_id (str): 任务ID
    
    Returns:
        ActionResponse: 包含任务结果的响应对象
    """
    try:
        from plugins.task_manager import TaskManager
        
        if not TaskManager.task_exists(task_id):
            return ActionResponse(
                action=Action.RESPONSE,
                result=None,
                response=f"任务ID '{task_id}' 不存在"
            )
        
        if not TaskManager.task_completed(task_id):
            return ActionResponse(
                action=Action.RESPONSE,
                result={"status": "running"},
                response=f"任务 '{task_id}' 仍在执行中"
            )
        
        result = TaskManager.get_task_result(task_id)
        
        if isinstance(result, ActionResponse):
            return result
        else:
            return ActionResponse(
                action=Action.RESPONSE,
                result=result,
                response=f"任务 '{task_id}' 执行结果: {result}"
            )
    except Exception as e:
        logger.error(f"查询MCP任务结果时出错: {str(e)}")
        return ActionResponse(
            action=Action.RESPONSE,
            result=None,
            response=f"查询MCP任务结果时出错: {str(e)}"
        )