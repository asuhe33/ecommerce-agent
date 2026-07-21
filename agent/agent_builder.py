"""Agent 构建模块：将 LLM、工具、提示词组装为完整的 LangChain Agent。"""

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import config
from agent.tools import ALL_TOOLS
from agent.prompts import SYSTEM_PROMPT


def build_agent() -> AgentExecutor:
    """构建并返回 AgentExecutor。

    使用 tool-calling agent 模式，LLM 根据用户问题自动选择工具。
    """
    # 1. 初始化 Ollama LLM
    llm = ChatOllama(
        model=config.LLM_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=0.1,  # 低温度，让输出更确定性
        num_predict=2048,  # 最大输出 token 数
    )

    # 2. 构建提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 3. 创建 tool-calling agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt,
    )

    # 4. 包装为 AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,  # 打印工具调用过程（调试用）
        max_iterations=5,  # 最多 5 步工具调用
        handle_parsing_errors=True,  # 处理 LLM 输出解析错误
    )

    return agent_executor


def run_cli():
    """命令行交互模式（用于 Day 2 测试）。"""
    from langchain_core.messages import HumanMessage, AIMessage

    print("=" * 50)
    print("🛒 电商 Agent — 命令行测试模式")
    print("输入问题进行对话，输入 'quit' 或 '退出' 结束")
    print("=" * 50)

    agent_executor = build_agent()
    chat_history = []

    while True:
        user_input = input("\n👤 您: ").strip()
        if user_input.lower() in ("quit", "退出", "q"):
            print("再见！")
            break
        if not user_input:
            continue

        try:
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history,
            })
            response = result.get("output", "抱歉，我无法处理您的请求。")
            print(f"\n🤖 助手: {response}")

            # 更新对话历史
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response))

        except Exception as e:
            print(f"\n❌ 出错: {e}")


if __name__ == "__main__":
    run_cli()
