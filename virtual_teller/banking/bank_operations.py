"""
银行操作处理模块
处理各种银行业务操作的安全检查和执行
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BankOperations:
    """
    银行操作处理类
    """
    
    # 定义安全操作列表
    SAFE_OPERATIONS = {
        "get_account_balance",
        "get_transaction_history",
        "get_financial_products",
        "get_loan_info",
        "guide_credit_card_application",
        "bank_policy_consultation"
    }
    
    # 需要额外验证的操作
    SENSITIVE_OPERATIONS = {
        "transfer_money",
        "withdraw_money",
        "change_password"
    }
    
    def __init__(self):
        """
        初始化银行操作处理器
        """
        self.operation_log = []
        
    def is_safe_operation(self, operation_name: str, args: Dict[str, Any]) -> bool:
        """
        检查操作是否安全
        
        Args:
            operation_name: 操作名称
            args: 操作参数
            
        Returns:
            bool: 是否为安全操作
        """
        # 检查是否在安全操作列表中
        if operation_name in self.SAFE_OPERATIONS:
            logger.info(f"Safe operation approved: {operation_name}")
            return True
            
        # 检查是否为敏感操作
        if operation_name in self.SENSITIVE_OPERATIONS:
            logger.warning(f"Sensitive operation requires additional verification: {operation_name}")
            # 敏感操作需要额外验证，这里默认不通过
            return False
            
        # 未知操作，默认不安全
        logger.warning(f"Unknown operation, treating as unsafe: {operation_name}")
        return False
        
    def log_operation(self, operation_name: str, args: Dict[str, Any], result: str):
        """
        记录操作日志
        
        Args:
            operation_name: 操作名称
            args: 操作参数
            result: 操作结果
        """
        log_entry = {
            "operation": operation_name,
            "args": args,
            "result": result
        }
        self.operation_log.append(log_entry)
        logger.info(f"Operation logged: {operation_name}")
        
    def get_account_balance(self, account_id: str) -> str:
        """
        查询账户余额
        
        Args:
            account_id: 账户ID
            
        Returns:
            str: 账户余额信息
        """
        # 这里应该是实际的银行API调用
        # 为了演示，我们返回模拟数据
        balance_info = f"您的账户 {account_id} 余额为 10,000.00 元。"
        self.log_operation("get_account_balance", {"account_id": account_id}, balance_info)
        return balance_info
        
    def get_transaction_history(self, account_id: str, limit: int = 5) -> str:
        """
        查询最近交易记录
        
        Args:
            account_id: 账户ID
            limit: 交易记录数量限制
            
        Returns:
            str: 交易记录信息
        """
        # 模拟交易记录
        transactions = [
            {"date": "2023-10-01", "type": "收入", "amount": "5000.00", "description": "工资"},
            {"date": "2023-10-02", "type": "支出", "amount": "120.50", "description": "超市购物"},
            {"date": "2023-10-03", "type": "支出", "amount": "80.00", "description": "餐饮"},
            {"date": "2023-10-05", "type": "支出", "amount": "200.00", "description": "加油"},
            {"date": "2023-10-06", "type": "收入", "amount": "3000.00", "description": "理财收益"}
        ][:limit]
        
        history = f"您账户 {account_id} 的最近 {len(transactions)} 笔交易记录：\n"
        for trans in transactions:
            history += f"{trans['date']}: {trans['type']} {trans['amount']}元 - {trans['description']}\n"
            
        self.log_operation("get_transaction_history", {"account_id": account_id, "limit": limit}, history)
        return history
        
    def get_financial_products(self, product_type: str = "all") -> str:
        """
        获取理财产品信息
        
        Args:
            product_type: 产品类型 (all, fund, insurance, deposit)
            
        Returns:
            str: 理财产品信息
        """
        products = {
            "fund": [
                {"name": "稳健增长基金", "risk": "低风险", "return_rate": "年化3.5%", "min_amount": "1000元"},
                {"name": "积极成长基金", "risk": "中风险", "return_rate": "年化5.2%", "min_amount": "5000元"}
            ],
            "insurance": [
                {"name": "终身寿险", "coverage": "身故保障", "premium": "年缴1000元起"},
                {"name": "重大疾病险", "coverage": "100种重疾保障", "premium": "年缴800元起"}
            ],
            "deposit": [
                {"name": "一年期定期存款", "rate": "2.1%", "min_amount": "50元"},
                {"name": "三年期定期存款", "rate": "2.75%", "min_amount": "50元"}
            ]
        }
        
        info = "我们为您推荐以下理财产品：\n\n"
        if product_type == "all" or product_type == "fund":
            info += "基金产品：\n"
            for fund in products["fund"]:
                info += f"- {fund['name']} ({fund['risk']})：{fund['return_rate']}，起购金额{fund['min_amount']}\n"
            info += "\n"
            
        if product_type == "all" or product_type == "insurance":
            info += "保险产品：\n"
            for insurance in products["insurance"]:
                info += f"- {insurance['name']}：{insurance['coverage']}，{insurance['premium']}\n"
            info += "\n"
            
        if product_type == "all" or product_type == "deposit":
            info += "存款产品：\n"
            for deposit in products["deposit"]:
                info += f"- {deposit['name']}：利率{deposit['rate']}，起存金额{deposit['min_amount']}\n"
            info += "\n"
            
        self.log_operation("get_financial_products", {"product_type": product_type}, info)
        return info