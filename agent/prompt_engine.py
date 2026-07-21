"""Prompt Engine：管理提示词模板、动态注入上下文、区分使用场景。

核心职责：
1. 管理所有提示词模板（系统提示词、工具提示词、RAG 提示词）
2. 根据场景动态选择模板
3. 注入动态上下文（检索结果、用户信息、历史对话等）
4. 支持模板版本管理和 A/B 测试
"""

from string import Template
from enum import Enum
from typing import Any


class PromptScene(Enum):
    """Prompt 使用场景枚举。"""
    SYSTEM = "system"                    # 主系统提示词
    RAG_QA = "rag_qa"                    # 知识问答场景
    CUSTOMER_SERVICE = "customer_service" # 客服场景
    TOOL_SELECTION = "tool_selection"    # 工具选择场景
    NO_RESULT = "no_result"              # 无结果兜底场景


# ── 提示词模板库 ──────────────────────────────────────────────

PROMPT_TEMPLATES = {
    # 主系统提示词
    PromptScene.SYSTEM: """你是一个专业的电商智能助手，为用户提供货品查询、货源查询、数据分析、知识问答和客服服务。

## 你可以使用的工具

1. **product_lookup** — 查询货品信息（价格、库存、分类、描述）
   - 当用户问商品价格、库存、分类、商品详情时使用

2. **supplier_lookup** — 查询供应商/货源信息
   - 当用户问商品供应商、供应商联系方式、供应商评分时使用

3. **data_analysis** — 数据分析（热销排行、分类统计、库存预警、订单统计）
   - 当用户问销售情况、什么卖得好、库存预警、订单数据时使用

4. **rag_qa** — 通用知识问答
   - 当用户问产品选购建议、平台使用规则、购物技巧等知识性问题时使用

5. **customer_service** — 客服服务
   - 当用户问退换货政策、物流配送、投诉建议、订单售后时使用

## 行为准则

1. 优先使用工具获取准确信息，不要凭空编造数据
2. 工具返回数据后，用自然语言总结给用户，保持友好简洁
3. 如果工具未找到结果，如实告知用户并给出建议
4. 回答要简洁明了，避免冗长
5. 涉及金额时保留两位小数
6. 不要透露系统内部实现细节（如数据库结构、SQL语句等）

## 语言风格

- 使用中文回答
- 称呼用户为"您"
- 语气专业友好，像一个经验丰富的电商客服""",

    # RAG 知识问答场景 — 引导 LLM 如何使用检索结果
    PromptScene.RAG_QA: """你是一个产品选购和平台使用顾问。

## 你的任务
根据以下知识库内容，回答用户的问题。

## 知识库内容
$context

## 回答规则
1. 优先从知识库内容中寻找答案
2. 如果知识库中有相关信息，基于内容回答并标注来源
3. 如果知识库中没有明确信息，如实告知"知识库中未找到相关信息"
4. 回答要简洁、专业、易懂
5. 涉及具体政策或规则时，引用原文内容

## 语言风格
- 使用中文回答
- 称呼用户为"您"
- 语气专业友好""",

    # 客服场景 — 更注重同理心和解决方案
    PromptScene.CUSTOMER_SERVICE: """你是一个专业的电商客服代表。

## 你的任务
根据以下客服知识库内容，解答用户的售后问题。

## 知识库内容
$context

## 回答规则
1. 优先从知识库内容中找到对应政策或流程
2. 先表达理解和同理心，再给出解决方案
3. 如果涉及退换货/退款，明确告知条件和流程
4. 如果知识库中没有明确信息，建议用户联系人工客服
5. 对于投诉类问题，先道歉再给出处理方案

## 语言风格
- 使用中文回答
- 称呼用户为"您"
- 语气亲切、耐心、有同理心
- 多用"非常抱歉给您带来不便"、"感谢您的理解"等礼貌用语""",

    # 工具选择引导
    PromptScene.TOOL_SELECTION: """根据用户的问题，选择最合适的工具。

## 工具选择规则
- 用户问具体商品的价格、库存 → product_lookup
- 用户问供应商是谁、联系方式 → supplier_lookup
- 用户问销售数据、排行榜、库存预警 → data_analysis
- 用户问选购建议、平台规则 → rag_qa
- 用户问退换货、物流、投诉 → customer_service""",

    # 无结果兜底
    PromptScene.NO_RESULT: """很抱歉，我暂时无法找到与您问题相关的信息。

## 建议
1. 您可以尝试换一种方式描述问题
2. 联系我们的客服热线：400-xxx-xxxx
3. 访问我们的帮助中心查看更多信息

请问还有其他我可以帮您的吗？""",
}


class PromptEngine:
    """提示词引擎：管理和渲染提示词模板。"""

    def __init__(self):
        self._templates = PROMPT_TEMPLATES
        self._version = "1.0.0"

    @property
    def version(self) -> str:
        """获取当前 Prompt 版本。"""
        return self._version

    def get_template(self, scene: PromptScene) -> str:
        """获取指定场景的提示词模板。"""
        return self._templates.get(scene, "")

    def render(self, scene: PromptScene, **kwargs) -> str:
        """渲染提示词模板，注入动态变量。

        Args:
            scene: 使用场景
            **kwargs: 模板变量，如 context="..."

        Returns:
            渲染后的提示词文本

        Example:
            >>> engine.render(PromptScene.RAG_QA, context="退货政策：7天无理由")
        """
        template = self.get_template(scene)
        if not template:
            return ""

        # 使用 string.Template 进行安全替换
        try:
            return Template(template).safe_substitute(**kwargs)
        except Exception:
            # 降级：直接字符串替换
            result = template
            for key, value in kwargs.items():
                result = result.replace(f"${key}", str(value))
            return result

    def get_rag_prompt(self, scene: PromptScene, context: str) -> str:
        """获取 RAG 场景的完整提示词（模板 + 检索上下文）。

        Args:
            scene: RAG_QA 或 CUSTOMER_SERVICE
            context: 知识库检索结果

        Returns:
            完整的 RAG 提示词
        """
        return self.render(scene, context=context)

    def get_system_prompt(self) -> str:
        """获取主系统提示词。"""
        return self.get_template(PromptScene.SYSTEM)

    def get_no_result_prompt(self) -> str:
        """获取无结果兜底提示词。"""
        return self.get_template(PromptScene.NO_RESULT)

    def list_scenes(self) -> list[str]:
        """列出所有可用场景。"""
        return [scene.value for scene in self._templates.keys()]

    def update_template(self, scene: PromptScene, template: str) -> None:
        """更新指定场景的模板（支持运行时热更新）。"""
        self._templates[scene] = template


# 全局单例
prompt_engine = PromptEngine()
