"""Agent 工具函数：5 个工具对应 5 个核心功能。

每个工具通过 @tool 装饰器注册，Agent 根据用户问题自动选择调用。
"""

from langchain_core.tools import tool

from database.db_manager import db_manager
from rag.retriever import format_search_results


@tool
def product_lookup(query: str) -> str:
    """查询货品信息。输入商品名称、关键词或分类，返回匹配的商品列表（名称、价格、库存、分类、描述）。
    适用于：查商品价格、查库存、按分类浏览商品、了解商品详情。"""
    sql = """
        SELECT name, category, price, stock, description
        FROM products
        WHERE name LIKE :kw OR category LIKE :kw OR description LIKE :kw
        LIMIT 10
    """
    results = db_manager.execute_query(sql, {"kw": f"%{query}%"})
    if not results:
        return f"未找到与「{query}」相关的商品。"

    parts = []
    for r in results:
        parts.append(
            f"商品：{r['name']}\n"
            f"  分类：{r['category']} | 价格：¥{r['price']} | 库存：{r['stock']}件\n"
            f"  简介：{r['description']}"
        )
    return "\n\n".join(parts)


@tool
def supplier_lookup(query: str) -> str:
    """查询货源/供应商信息。输入供应商名称或商品名，返回供应商详情（名称、联系人、电话、地址、评分）。
    适用于：查找商品供应商、了解供应商联系方式、查看供应商评分。"""
    # 先尝试按供应商名查
    sql_by_name = """
        SELECT id, name, contact, phone, address, rating
        FROM suppliers
        WHERE name LIKE :kw OR contact LIKE :kw
        LIMIT 10
    """
    results = db_manager.execute_query(sql_by_name, {"kw": f"%{query}%"})

    # 如果没找到，尝试按商品名找到对应供应商
    if not results:
        sql_by_product = """
            SELECT s.id, s.name, s.contact, s.phone, s.address, s.rating
            FROM suppliers s
            JOIN products p ON p.supplier_id = s.id
            WHERE p.name LIKE :kw OR p.category LIKE :kw
            LIMIT 10
        """
        results = db_manager.execute_query(sql_by_product, {"kw": f"%{query}%"})

    if not results:
        return f"未找到与「{query}」相关的供应商。"

    parts = []
    for r in results:
        parts.append(
            f"供应商：{r['name']}\n"
            f"  联系人：{r['contact']} | 电话：{r['phone']}\n"
            f"  地址：{r['address']} | 评分：{r['rating']}/5.0"
        )
    return "\n\n".join(parts)


@tool
def data_analysis(query: str) -> str:
    """数据分析：根据自然语言描述执行销售统计、热销排行、库存分析等。
    适用于：查看热销商品、统计销售额、分析分类销售情况、库存预警。

    支持的分析类型：
    - 热销排行：销量最高的商品
    - 分类统计：各分类的销售额/销量
    - 库存预警：库存低于阈值的商品
    - 订单统计：订单数量、总金额等"""
    query_lower = query.lower()

    # 根据关键词选择预定义分析模板
    if any(kw in query_lower for kw in ["热销", "卖得最好", "销量最高", "top"]):
        sql = """
            SELECT p.name, p.category, SUM(oi.quantity) AS total_qty, SUM(oi.quantity * oi.unit_price) AS total_revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status != '已取消'
            GROUP BY p.id
            ORDER BY total_qty DESC
            LIMIT 10
        """
        results = db_manager.execute_query(sql)
        if not results:
            return "暂无销售数据。"
        parts = ["📊 热销商品排行榜（按销量）：\n"]
        for i, r in enumerate(results, 1):
            parts.append(
                f"{i}. {r['name']}（{r['category']}）\n"
                f"   销量：{r['total_qty']}件 | 销售额：¥{r['total_revenue']:,.2f}"
            )
        return "\n".join(parts)

    elif any(kw in query_lower for kw in ["分类", "品类", "category"]):
        sql = """
            SELECT p.category,
                   COUNT(DISTINCT oi.order_id) AS order_count,
                   SUM(oi.quantity) AS total_qty,
                   SUM(oi.quantity * oi.unit_price) AS total_revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status != '已取消'
            GROUP BY p.category
            ORDER BY total_revenue DESC
        """
        results = db_manager.execute_query(sql)
        if not results:
            return "暂无分类销售数据。"
        parts = ["📊 分类销售统计：\n"]
        for r in results:
            parts.append(
                f"• {r['category']}\n"
                f"  订单数：{r['order_count']} | 销量：{r['total_qty']}件 | 销售额：¥{r['total_revenue']:,.2f}"
            )
        return "\n".join(parts)

    elif any(kw in query_lower for kw in ["库存", "预警", "缺货", "stock"]):
        threshold = 20
        # 尝试从 query 中提取数字作为阈值
        import re
        numbers = re.findall(r'\d+', query)
        if numbers:
            threshold = int(numbers[0])
        sql = """
            SELECT name, category, stock, price
            FROM products
            WHERE stock <= :threshold
            ORDER BY stock ASC
            LIMIT 15
        """
        results = db_manager.execute_query(sql, {"threshold": threshold})
        if not results:
            return f"✅ 所有商品库存均高于 {threshold} 件，无库存预警。"
        parts = [f"⚠️ 库存预警（库存 ≤ {threshold} 件）：\n"]
        for r in results:
            parts.append(f"• {r['name']}（{r['category']}）- 库存：{r['stock']}件 - ¥{r['price']}")
        return "\n".join(parts)

    elif any(kw in query_lower for kw in ["订单", "总额", "金额", "order"]):
        sql = """
            SELECT COUNT(*) AS total_orders,
                   SUM(total_amount) AS total_revenue,
                   AVG(total_amount) AS avg_amount
            FROM orders
            WHERE status != '已取消'
        """
        r = db_manager.execute_query(sql)[0]
        return (
            f"📊 订单统计：\n"
            f"  总订单数：{r['total_orders']}\n"
            f"  总销售额：¥{r['total_revenue']:,.2f}\n"
            f"  平均客单价：¥{r['avg_amount']:,.2f}"
        )

    else:
        # 默认返回订单总览
        sql = """
            SELECT status, COUNT(*) AS count
            FROM orders
            GROUP BY status
        """
        results = db_manager.execute_query(sql)
        parts = ["📊 订单状态概览：\n"]
        for r in results:
            parts.append(f"• {r['status']}：{r['count']}单")
        parts.append("\n提示：您可以问'热销排行'、'分类统计'、'库存预警'、'订单统计'等。")
        return "\n".join(parts)


@tool
def rag_qa(query: str) -> str:
    """通用知识问答：回答产品选购建议、平台使用规则、购物技巧等知识性问题。
    适用于：如何选手机、如何注册账号、如何使用优惠券、购物技巧等。"""
    return format_search_results(query, k=5)


@tool
def customer_service(query: str) -> str:
    """客服服务：回答退换货政策、物流配送、投诉建议、订单售后等客服问题。
    适用于：退货流程、换货条件、物流查询、运费规则、投诉处理等。"""
    return format_search_results(query, k=5)


# 工具列表（供 Agent 构建时使用）
ALL_TOOLS = [product_lookup, supplier_lookup, data_analysis, rag_qa, customer_service]
