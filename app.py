"""电商 Agent — Streamlit Web 界面。

启动命令:
    streamlit run app.py
"""

import streamlit as st
import time

from agent.agent_builder import build_agent
from utils.ollama_helper import ensure_models

# ── 页面配置 ──────────────────────────────────────────────

st.set_page_config(
    page_title="电商智能助手",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 侧边栏 ────────────────────────────────────────────────

with st.sidebar:
    st.title("🛒 电商智能助手")
    st.markdown("---")

    # 模型状态检查
    with st.expander("⚙️ 系统状态", expanded=True):
        if st.button("检查 Ollama 连接", key="check_ollama"):
            with st.spinner("检查中..."):
                if ensure_models():
                    st.success("✅ 系统就绪")
                else:
                    st.error("❌ 模型未就绪，请检查 Ollama")

    st.markdown("---")
    st.markdown("### 💬 功能说明")
    st.markdown("""
    - **货品查询**：商品价格、库存、分类
    - **货源查询**：供应商信息、联系方式
    - **数据分析**：热销排行、分类统计、库存预警
    - **知识问答**：产品选购、平台规则
    - **客服服务**：退换货、物流、投诉
    """)

    st.markdown("---")
    st.markdown("### 📝 示例问题")
    st.markdown("""
    - iPhone 15 多少钱？有货吗？
    - 最近什么商品卖得最好？
    - 你们的退货政策是什么？
    - 华为手机的供应商是谁？
    - 有哪些库存预警的商品？
    """)

    # 清空对话按钮
    st.markdown("---")
    if st.button("🗑️ 清空对话", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.agent_executor = None
        st.rerun()

# ── 主界面 ────────────────────────────────────────────────

st.title("🛒 电商智能助手")
st.markdown("您好！我是您的电商智能助手，可以帮您查询商品、分析数据、解答问题。")

# 初始化 Agent（懒加载，首次对话时创建）
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── 用户输入处理 ──────────────────────────────────────────

if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示助手思考中
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 思考中...")

        try:
            # 首次使用时构建 Agent
            if st.session_state.agent_executor is None:
                with st.spinner("正在初始化 Agent..."):
                    st.session_state.agent_executor = build_agent()

            agent_executor = st.session_state.agent_executor

            # 构建对话历史（传给 Agent）
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history = []
            for msg in st.session_state.messages[:-1]:  # 排除当前用户消息
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))

            # 调用 Agent
            start_time = time.time()
            result = agent_executor.invoke({
                "input": prompt,
                "chat_history": chat_history,
            })
            response = result.get("output", "抱歉，我无法处理您的请求。")
            elapsed = round(time.time() - start_time, 1)

            # 流式输出效果
            full_response = ""
            for char in response:
                full_response += char
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)

            message_placeholder.markdown(full_response)
            st.caption(f"⏱️ 耗时 {elapsed} 秒")

            # 保存到历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
            })

        except Exception as e:
            error_msg = f"❌ 出错了：{str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
            })
