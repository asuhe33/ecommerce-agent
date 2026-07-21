"""Agent 系统提示词：定义角色、工具使用规则和行为约束。

本模块保留向后兼容，新代码请使用 agent.prompt_engine.prompt_engine。
"""

from agent.prompt_engine import prompt_engine, PromptScene

# 向后兼容：导出系统提示词
SYSTEM_PROMPT = prompt_engine.get_system_prompt()

# 导出场景枚举（方便其他模块使用）
__all__ = ["SYSTEM_PROMPT", "prompt_engine", "PromptScene"]
