"""
合规检查器
确保虚拟柜员的响应符合银行法规和合规要求
"""

import logging
import re

logger = logging.getLogger(__name__)

class ComplianceChecker:
    """
    合规检查器类
    """
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # 信用卡号模式
        r'\b\d{16,19}\b',  # 银行卡号模式
        r'\b\d{6}\b',  # 密码模式
        r'password|passwd|pwd',  # 密码关键词
        r'secret|private',  # 私密信息关键词
    ]
    
    # 合规关键词
    COMPLIANCE_REQUIRED_PHRASES = [
        "根据监管要求",
        "风险提示",
        "请您注意",
        "建议您",
        "请注意"
    ]
    
    def __init__(self):
        """
        初始化合规检查器
        """
        self.blocked_words = [
            "内部信息", "机密", "绝密", "内部资料", 
            "员工专用", "仅限内部", "未公开信息"
        ]
        
        self.warning_words = [
            "保证收益", "无风险", "100%安全", "绝对可靠"
        ]
        
    def check_query_compliance(self, query: str) -> bool:
        """
        检查用户查询是否合规
        
        Args:
            query: 用户查询内容
            
        Returns:
            bool: 是否合规
        """
        query_lower = query.lower()
        
        # 检查是否包含禁止的词汇
        for word in self.blocked_words:
            if word in query_lower:
                logger.warning(f"Query contains blocked word: {word}")
                return False
                
        # 检查是否试图获取敏感信息
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Query contains sensitive pattern: {pattern}")
                return False
                
        logger.info("Query compliance check passed")
        return True
        
    def check_response_compliance(self, response: str) -> bool:
        """
        检查系统响应是否合规
        
        Args:
            response: 系统响应内容
            
        Returns:
            bool: 是否合规
        """
        response_lower = response.lower()
        
        # 检查是否包含禁止的词汇
        for word in self.blocked_words:
            if word in response_lower:
                logger.warning(f"Response contains blocked word: {word}")
                return False
                
        # 检查是否包含风险过低的表述
        for word in self.warning_words:
            if word in response_lower:
                logger.warning(f"Response contains risky word: {word}")
                return False
                
        # 检查是否泄露敏感信息
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                logger.warning(f"Response contains sensitive pattern: {pattern}")
                return False
                
        logger.info("Response compliance check passed")
        return True
        
    def add_blocked_word(self, word: str):
        """
        添加禁止词汇
        
        Args:
            word: 要添加的禁止词汇
        """
        if word not in self.blocked_words:
            self.blocked_words.append(word)
            logger.info(f"Added blocked word: {word}")
            
    def add_warning_word(self, word: str):
        """
        添加风险词汇
        
        Args:
            word: 要添加的风险词汇
        """
        if word not in self.warning_words:
            self.warning_words.append(word)
            logger.info(f"Added warning word: {word}")