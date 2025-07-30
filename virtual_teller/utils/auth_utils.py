"""
身份验证工具模块
处理虚拟柜员系统中的身份验证相关功能
"""

import logging
import hashlib
import secrets
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """身份验证管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化身份验证管理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.sessions = {}  # 存储会话信息
        self.max_failed_attempts = config.get("Banking", {}).get("authentication", {}).get("max_failed_attempts", 3)
        self.failed_attempts = {}  # 存储失败尝试次数
        
    def generate_session_token(self) -> str:
        """
        生成会话令牌
        
        Returns:
            str: 会话令牌
        """
        token = secrets.token_urlsafe(32)
        return token
    
    def create_session(self, customer_id: str, auth_level: str = "basic") -> str:
        """
        创建用户会话
        
        Args:
            customer_id: 客户ID
            auth_level: 认证级别 (basic: 基础, enhanced: 增强, full: 完全)
            
        Returns:
            str: 会话令牌
        """
        token = self.generate_session_token()
        session_data = {
            "customer_id": customer_id,
            "auth_level": auth_level,
            "created_time": time.time(),
            "last_activity": time.time()
        }
        self.sessions[token] = session_data
        logger.info(f"为客户 {customer_id} 创建会话，认证级别: {auth_level}")
        return token
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证会话有效性
        
        Args:
            token: 会话令牌
            
        Returns:
            Optional[Dict[str, Any]]: 会话数据，如果无效则返回None
        """
        if token not in self.sessions:
            logger.warning(f"会话令牌无效: {token}")
            return None
            
        session = self.sessions[token]
        
        # 检查会话是否过期 (10分钟)
        session_timeout = self.config.get("Banking", {}).get("security", {}).get("session_timeout_minutes", 10) * 60
        if time.time() - session["last_activity"] > session_timeout:
            del self.sessions[token]
            logger.warning(f"会话已过期: {token}")
            return None
            
        # 更新最后活动时间
        session["last_activity"] = time.time()
        return session
    
    def close_session(self, token: str) -> bool:
        """
        关闭会话
        
        Args:
            token: 会话令牌
            
        Returns:
            bool: 是否成功关闭
        """
        if token in self.sessions:
            del self.sessions[token]
            logger.info(f"会话已关闭: {token}")
            return True
        return False
    
    def record_failed_attempt(self, identifier: str):
        """
        记录失败尝试
        
        Args:
            identifier: 标识符 (如客户ID或IP地址)
        """
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = 0
        self.failed_attempts[identifier] += 1
        logger.warning(f"记录失败尝试: {identifier}, 次数: {self.failed_attempts[identifier]}")
    
    def is_locked_out(self, identifier: str) -> bool:
        """
        检查是否被锁定
        
        Args:
            identifier: 标识符
            
        Returns:
            bool: 是否被锁定
        """
        return self.failed_attempts.get(identifier, 0) >= self.max_failed_attempts
    
    def reset_failed_attempts(self, identifier: str):
        """
        重置失败尝试次数
        
        Args:
            identifier: 标识符
        """
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
            logger.info(f"重置失败尝试次数: {identifier}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """
        哈希密码
        
        Args:
            password: 原始密码
            salt: 盐值，如果为None则自动生成
            
        Returns:
            tuple: (哈希值, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('ascii'), 100000)
        return pwdhash.hex(), salt