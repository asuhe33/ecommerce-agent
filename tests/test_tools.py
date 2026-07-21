"""测试 agent/tools.py — 5 个工具函数。"""

import pytest
from unittest.mock import patch

from agent.tools import (
    ALL_TOOLS,
    customer_service,
    data_analysis,
    product_lookup,
    rag_qa,
    supplier_lookup,
)
from langchain_core.tools import BaseTool

# ── Mock 数据（字段名与实际 SQL 查询结果匹配）─────────────────

MOCK_PRODUCTS = [
    {
        "name": "智能手机 Pro",
        "category": "电子产品",
        "price": 4999.00,
        "stock": 50,
        "description": "6.7英寸全面屏，128GB存储",
    },
    {
        "name": "蓝牙耳机",
        "category": "电子产品",
        "price": 299.00,
        "stock": 200,
        "description": "降噪，续航30小时",
    },
]

MOCK_SUPPLIERS = [
    {
        "id": 1,
        "name": "深圳科技有限公司",
        "contact": "张经理",
        "phone": "13800138000",
        "address": "深圳市南山区科技园",
        "rating": 4.80,
    }
]

MOCK_HOT_SALES = [
    {"name": "智能手机 Pro", "category": "电子产品", "total_qty": 150, "total_revenue": 749850.0},
    {"name": "蓝牙耳机", "category": "电子产品", "total_qty": 100, "total_revenue": 29900.0},
]

MOCK_CATEGORY_STATS = [
    {"category": "电子产品", "order_count": 80, "total_qty": 250, "total_revenue": 779750.0},
]

MOCK_LOW_STOCK = [
    {"name": "智能手表", "category": "电子产品", "stock": 5, "price": 1299.0},
]

MOCK_ORDER_STATS = [
    {"total_orders": 200, "total_revenue": 500000.0, "avg_amount": 2500.0},
]

MOCK_ORDER_STATUS = [
    {"status": "已完成", "count": 150},
    {"status": "待发货", "count": 30},
    {"status": "已取消", "count": 20},
]

MOCK_KB_RESULTS = [
    {
        "content": "自收到商品之日起7天内，可无理由退货。",
        "source": "return_policy.txt",
        "score": 0.85,
    },
    {
        "content": "退货商品需保持原包装完好。",
        "source": "return_policy.txt",
        "score": 0.72,
    },
]


# ── 1. 工具注册验证 ────────────────────────────────────────


class TestToolRegistration:
    """验证所有工具已正确注册。"""

    def test_all_tools_has_5_items(self):
        assert len(ALL_TOOLS) == 5

    def test_all_tools_are_base_tool_instances(self):
        for tool in ALL_TOOLS:
            assert isinstance(tool, BaseTool)

    def test_tool_names(self):
        names = {t.name for t in ALL_TOOLS}
        expected = {
            "product_lookup",
            "supplier_lookup",
            "data_analysis",
            "rag_qa",
            "customer_service",
        }
        assert names == expected

    def test_tool_descriptions_exist(self):
        for tool in ALL_TOOLS:
            assert tool.description
            assert len(tool.description) > 10


# ── 2. product_lookup 测试 ─────────────────────────────────


class TestProductLookup:
    """测试货品查询工具。"""

    def test_returns_formatted_products(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_PRODUCTS

            result = product_lookup.run("手机")

            assert "智能手机 Pro" in result
            assert "4999.00" in result or "4999.0" in result
            assert "50件" in result
            mock_db.execute_query.assert_called_once()

    def test_no_result_returns_friendly_message(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = []

            result = product_lookup.run("不存在的商品")

            assert "未找到" in result

    def test_query_passed_as_parameter(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = []

            product_lookup.run("耳机")

            call_args = mock_db.execute_query.call_args
            assert "耳机" in str(call_args)


# ── 3. supplier_lookup 测试 ─────────────────────────────────


class TestSupplierLookup:
    """测试货源查询工具。"""

    def test_returns_formatted_suppliers(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_SUPPLIERS

            result = supplier_lookup.run("深圳")

            assert "深圳科技有限公司" in result
            assert "张经理" in result
            mock_db.execute_query.assert_called_once()

    def test_no_result_returns_friendly_message(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = []

            result = supplier_lookup.run("不存在的供应商")

            assert "未找到" in result

    def test_fallback_to_product_search(self):
        """供应商名无结果时，回退到商品名搜索。"""
        with patch("agent.tools.db_manager") as mock_db:
            # 第一次返回空，第二次返回结果
            mock_db.execute_query.side_effect = [[], MOCK_SUPPLIERS]

            result = supplier_lookup.run("手机")

            assert "深圳科技有限公司" in result
            assert mock_db.execute_query.call_count == 2


# ── 4. data_analysis 测试 ───────────────────────────────────


class TestDataAnalysis:
    """测试数据分析工具 — 4 个分支 + 默认。"""

    def test_hot_sales_branch(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_HOT_SALES

            result = data_analysis.run("热销商品有哪些？")

            assert "热销" in result
            assert "智能手机 Pro" in result
            assert "150件" in result

    def test_category_stats_branch(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_CATEGORY_STATS

            result = data_analysis.run("商品分类统计")

            assert "电子产品" in result
            assert "80" in result  # order_count

    def test_low_stock_branch(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_LOW_STOCK

            result = data_analysis.run("库存预警")

            assert "库存" in result or "预警" in result
            assert "智能手表" in result

    def test_low_stock_with_custom_threshold(self):
        """从查询中提取自定义阈值。"""
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = []

            data_analysis.run("库存少于10件的商品")

            call_args = mock_db.execute_query.call_args
            assert "10" in str(call_args)

    def test_low_stock_default_threshold(self):
        """默认阈值为 20。"""
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = []

            data_analysis.run("库存预警")

            call_args = mock_db.execute_query.call_args
            assert "20" in str(call_args)

    def test_order_stats_branch(self):
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_ORDER_STATS

            result = data_analysis.run("订单统计")

            assert "订单" in result
            assert "200" in result  # total_orders

    def test_default_branch(self):
        """未匹配关键词时返回订单状态概览。"""
        with patch("agent.tools.db_manager") as mock_db:
            mock_db.execute_query.return_value = MOCK_ORDER_STATUS

            result = data_analysis.run("随便说点什么")

            assert "订单状态概览" in result
            assert "热销排行" in result  # 提示信息


# ── 5. rag_qa / customer_service 测试 ───────────────────────


class TestRagTools:
    """测试 RAG 问答和客服工具。"""

    def test_rag_qa_calls_formatter(self):
        with patch("agent.tools.format_search_results") as mock_fmt:
            mock_fmt.return_value = "退货政策：7天无理由退货。"

            result = rag_qa.run("如何退货？")

            mock_fmt.assert_called_once_with("如何退货？", k=5)
            assert result == "退货政策：7天无理由退货。"

    def test_customer_service_calls_formatter(self):
        with patch("agent.tools.format_search_results") as mock_fmt:
            mock_fmt.return_value = "快递一般3-5天到达。"

            result = customer_service.run("快递多久到？")

            mock_fmt.assert_called_once_with("快递多久到？", k=5)
            assert result == "快递一般3-5天到达。"

    def test_rag_and_customer_service_are_identical(self):
        """验证 rag_qa 和 customer_service 行为一致（设计缺陷标记）。"""
        with patch("agent.tools.format_search_results") as mock_fmt:
            mock_fmt.return_value = "测试结果"

            r1 = rag_qa.run("测试问题")
            r2 = customer_service.run("测试问题")

            assert r1 == r2
