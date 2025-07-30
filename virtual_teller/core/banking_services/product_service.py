"""
产品服务模块
处理银行产品推荐和查询服务
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ProductService:
    """产品服务类"""
    
    def __init__(self):
        """初始化产品服务"""
        pass
    
    def get_financial_products(self, product_type: str = "all") -> Dict[str, Any]:
        """
        获取理财产品信息
        
        Args:
            product_type: 产品类型 (fund: 基金, insurance: 保险, deposit: 存款, all: 全部)
            
        Returns:
            Dict[str, Any]: 理财产品信息
        """
        # 模拟理财产品数据
        products = {
            "fund": [
                {
                    "product_id": "F001",
                    "name": "稳健增长混合型基金",
                    "type": "基金",
                    "risk_level": "低风险",
                    "annual_return_rate": "3.5%",
                    "min_amount": 1000.00,
                    "description": "主要投资于债券等固定收益类资产，风险较低，收益稳定"
                },
                {
                    "product_id": "F002",
                    "name": "积极成长股票型基金",
                    "type": "基金",
                    "risk_level": "中高风险",
                    "annual_return_rate": "5.2%",
                    "min_amount": 5000.00,
                    "description": "主要投资于优质股票，追求长期资本增值"
                }
            ],
            "insurance": [
                {
                    "product_id": "I001",
                    "name": "终身寿险",
                    "type": "保险",
                    "coverage": "身故保障",
                    "premium": "年缴1000元起",
                    "description": "提供终身身故保障，可传承财富"
                },
                {
                    "product_id": "I002",
                    "name": "重大疾病保险",
                    "type": "保险",
                    "coverage": "100种重疾保障",
                    "premium": "年缴800元起",
                    "description": "确诊即赔，覆盖多种重大疾病"
                }
            ],
            "deposit": [
                {
                    "product_id": "D001",
                    "name": "一年期定期存款",
                    "type": "存款",
                    "interest_rate": "2.1%",
                    "min_amount": 50.00,
                    "description": "保本保息，到期一次性还本付息"
                },
                {
                    "product_id": "D002",
                    "name": "三年期定期存款",
                    "type": "存款",
                    "interest_rate": "2.75%",
                    "min_amount": 50.00,
                    "description": "利率较高，适合长期资金规划"
                }
            ]
        }
        
        if product_type == "all":
            financial_products = {
                "products": products,
                "total_count": sum(len(products[ptype]) for ptype in products)
            }
        else:
            financial_products = {
                "products": {product_type: products.get(product_type, [])},
                "total_count": len(products.get(product_type, []))
            }
        
        logger.info(f"获取理财产品信息: {product_type}")
        return financial_products
    
    def get_loan_products(self, loan_type: str = "all") -> Dict[str, Any]:
        """
        获取贷款产品信息
        
        Args:
            loan_type: 贷款类型 (mortgage: 房贷, personal: 个人贷, business: 经营贷, all: 全部)
            
        Returns:
            Dict[str, Any]: 贷款产品信息
        """
        # 模拟贷款产品数据
        loans = {
            "mortgage": [
                {
                    "product_id": "L001",
                    "name": "首套房贷款",
                    "type": "房贷",
                    "interest_rate": "4.2%",
                    "term": "30年",
                    "description": "购买首套住房的优惠贷款"
                },
                {
                    "product_id": "L002",
                    "name": "二手房贷款",
                    "type": "房贷",
                    "interest_rate": "4.5%",
                    "term": "30年",
                    "description": "购买二手房的专项贷款"
                }
            ],
            "personal": [
                {
                    "product_id": "L003",
                    "name": "个人消费贷款",
                    "type": "个人贷",
                    "interest_rate": "5.5%",
                    "term": "5年",
                    "description": "用于个人消费的信用贷款"
                },
                {
                    "product_id": "L004",
                    "name": "个人装修贷款",
                    "type": "个人贷",
                    "interest_rate": "4.8%",
                    "term": "3年",
                    "description": "专门用于房屋装修的贷款"
                }
            ],
            "business": [
                {
                    "product_id": "L005",
                    "name": "小微企业贷款",
                    "type": "经营贷",
                    "interest_rate": "4.9%",
                    "term": "5年",
                    "description": "支持小微企业发展的经营贷款"
                }
            ]
        }
        
        if loan_type == "all":
            loan_products = {
                "products": loans,
                "total_count": sum(len(loans[ltype]) for ltype in loans)
            }
        else:
            loan_products = {
                "products": {loan_type: loans.get(loan_type, [])},
                "total_count": len(loans.get(loan_type, []))
            }
        
        logger.info(f"获取贷款产品信息: {loan_type}")
        return loan_products
    
    def get_credit_cards(self) -> Dict[str, Any]:
        """
        获取信用卡产品信息
        
        Returns:
            Dict[str, Any]: 信用卡产品信息
        """
        # 模拟信用卡产品数据
        credit_cards = [
            {
                "card_id": "C001",
                "name": "金卡",
                "annual_fee": "300元",
                "features": ["机场贵宾厅", "积分兑换", "免费体检"],
                "description": "适合有一定消费能力的客户"
            },
            {
                "card_id": "C002",
                "name": "白金卡",
                "annual_fee": "1000元",
                "features": ["无限次机场贵宾厅", "高额航空意外险", "专属客服", "免费体检", "高尔夫练习场"],
                "description": "为高端客户提供全方位尊享服务"
            }
        ]
        
        credit_card_info = {
            "cards": credit_cards,
            "total_count": len(credit_cards)
        }
        
        logger.info("获取信用卡产品信息")
        return credit_card_info