"""
AI Customer Service Chat Interface - User Chat Page
使用者聊天頁面（公開，無需密碼）
"""

import streamlit as st
import requests
import os
import sys
from datetime import datetime

# Add parent directory to path for importing feedback_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import feedback database
try:
    from customer_feedback_db import feedback_db
except:
    feedback_db = None

# Page configuration
st.set_page_config(
    page_title="AI 聊天助理",
    page_icon="💬",
    layout="wide",
)

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")


# Fallback answer function (when OpenAI API is unavailable)
def get_fallback_answer(user_input: str) -> str:
    """
    簡單的規則匹配備用回答（當 OpenAI API 不可用時）
    """
    user_input_lower = user_input.lower()

    # 訂單相關
    if any(
        keyword in user_input for keyword in ["訂單", "出貨", "配送", "物流", "運送"]
    ):
        return "關於訂單查詢，您可以：\n1. 登入會員帳號查看訂單狀態\n2. 使用訂單編號追蹤物流\n3. 聯繫客服：service@example.com\n\n如需更詳細的協助，請提供您的訂單編號。"

    # 退換貨相關
    elif any(
        keyword in user_input
        for keyword in ["退貨", "退款", "換貨", "退換", "瑕疵", "不滿意"]
    ):
        return "關於退換貨服務：\n1. 商品到貨7天內可申請退換貨\n2. 商品需保持完整包裝\n3. 請聯繫客服申請退換貨\n\n客服信箱：service@example.com\n客服電話：0800-123-456"

    # 產品相關
    elif any(
        keyword in user_input
        for keyword in ["產品", "商品", "規格", "功能", "尺寸", "顏色", "材質"]
    ):
        return "關於產品資訊：\n1. 您可以在商品頁面查看詳細規格\n2. 如有特殊需求，請聯繫客服\n3. 我們提供專業的產品諮詢服務\n\n需要更多協助嗎？請告訴我具體的產品名稱。"

    # 帳號相關
    elif any(
        keyword in user_input for keyword in ["帳號", "密碼", "登入", "註冊", "會員"]
    ):
        return "關於帳號問題：\n1. 忘記密碼：點擊登入頁面的「忘記密碼」\n2. 註冊會員：點擊「立即註冊」\n3. 帳號問題：請聯繫客服協助\n\n客服信箱：service@example.com"

    # 營業時間
    elif any(
        keyword in user_input for keyword in ["營業時間", "上班時間", "幾點", "時間"]
    ):
        return "我們的營業時間：\n- 週一至週五：09:00 - 18:00\n- 週六：10:00 - 17:00\n- 週日及國定假日：休息\n\n線上客服24小時為您服務！"

    # 聯絡方式
    elif any(
        keyword in user_input for keyword in ["聯絡", "聯繫", "電話", "信箱", "客服"]
    ):
        return "聯絡我們：\n📧 信箱：service@example.com\n📞 電話：0800-123-456\n💬 線上客服：24小時服務\n\n我們會盡快回覆您的問題！"

    # 運費相關
    elif any(keyword in user_input for keyword in ["運費", "郵資", "免運", "配送費"]):
        return "運費說明：\n- 訂單滿 $1000 免運費\n- 未滿 $1000，運費 $100\n- 離島地區運費另計\n\n更多運送資訊請參考購物說明。"

    # 付款相關
    elif any(
        keyword in user_input
        for keyword in ["付款", "支付", "刷卡", "轉帳", "貨到付款"]
    ):
        return "付款方式：\n1. 信用卡付款\n2. ATM 轉帳\n3. 超商取貨付款\n4. 貨到付款\n\n所有付款方式都很安全，請放心使用！"

    # 優惠相關
    elif any(
        keyword in user_input for keyword in ["優惠", "折扣", "促銷", "活動", "折價"]
    ):
        return "目前優惠活動：\n1. 新會員首購優惠\n2. 滿額贈品活動\n3. 季節性折扣\n\n詳細優惠請查看官網首頁，或訂閱電子報獲得最新資訊！"

    # 預設回答
    else:
        return "感謝您的提問！由於目前系統負載較高，我暫時無法提供詳細回答。\n\n您可以：\n1. 📧 發送郵件至：service@example.com\n2. 📞 撥打客服專線：0800-123-456\n3. 💬 稍後再試使用線上客服\n\n我們會盡快為您解答！"


# Custom CSS for chat interface
st.markdown(
    """
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .emotion-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .emotion-positive {
        background-color: #4caf50;
        color: white;
    }
    .emotion-neutral {
        background-color: #ff9800;
        color: white;
    }
    .emotion-negative {
        background-color: #f44336;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar with navigation
with st.sidebar:
    st.markdown("### 🧭 導航")
    if st.button("🏠 返回首頁  ", use_container_width=True, type="primary"):
        st.switch_page("streamlit_app.py")

    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.info(
        "💬 直接輸入您的問題\n\n"
        "🎯 我可以幫您：\n"
        "- 查詢訂單\n"
        "- 產品諮詢\n"
        "- 退換貨問題\n"
        "- 其他客服問題"
    )

# Title and navigation
col1, col2 = st.columns([4, 1])
with col1:
    st.title("💬 AI 客服聊天助理")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    if st.button("🏠 返回首頁", key="top_home_button"):
        st.switch_page("streamlit_app.py")

st.markdown("歡迎使用！我是您的 AI 助理，有任何問題都可以問我 😊")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "您好！我是 AI 客服助理，很高興為您服務。請問有什麼可以幫助您的嗎？",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Display emotion badge if available
        if "emotion" in message and message["role"] == "user":
            emotion = message["emotion"]
            emotion_class = (
                f"emotion-{emotion.lower()}"
                if emotion.lower() in ["positive", "neutral", "negative"]
                else "emotion-neutral"
            )
            emotion_text = {
                "正面": "😊 正面",
                "中性": "😐 中性",
                "負面": "😞 負面",
            }.get(emotion, emotion)

            st.markdown(
                f'<span class="emotion-badge {emotion_class}">{emotion_text}</span>',
                unsafe_allow_html=True,
            )

        # Display timestamp
        st.caption(message.get("timestamp", ""))

# Handle quick questions first
if "quick_question" in st.session_state and st.session_state.quick_question:
    user_input = st.session_state.quick_question
    st.session_state.quick_question = None
else:
    # Chat input
    user_input = st.chat_input("請輸入您的問題...")

if user_input:
    # Add user message to chat history
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
        st.caption(timestamp)

    # Call API to get response
    with st.chat_message("assistant"):
        with st.spinner("正在思考中..."):
            try:
                # Call the chat API
                response = requests.post(
                    f"{API_URL}/chat", json={"text": user_input}, timeout=30
                )

                if response.status_code == 200:
                    result = response.json()

                    # Extract information
                    answer = result.get("answer", "抱歉，我無法回答這個問題。")
                    emotion = result.get("emotion", {}).get("emotion", "未知")
                    intent = result.get("intent", {}).get("intent", "未知")

                    # Display answer
                    st.write(answer)

                    # Display metadata in expander
                    with st.expander("📊 查看分析詳情"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("情緒", emotion)
                        with col2:
                            st.metric("意圖", intent)

                        if "retrieved_faqs" in result and result["retrieved_faqs"]:
                            st.markdown("**參考來源：**")
                            for i, faq in enumerate(result["retrieved_faqs"], 1):
                                st.markdown(f"{i}. {faq.get('question', 'N/A')}")

                    st.caption(datetime.now().strftime("%H:%M:%S"))

                    # Save to feedback database
                    if feedback_db:
                        try:
                            # Get or create session ID
                            if "session_id" not in st.session_state:
                                st.session_state.session_id = (
                                    f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                )

                            feedback_db.add_feedback(
                                user_message=user_input,
                                emotion=emotion,
                                emotion_confidence=result.get("emotion", {}).get(
                                    "confidence", 0
                                ),
                                intent=intent,
                                session_id=st.session_state.session_id,
                            )
                        except Exception as e:
                            # 靜默失敗，不影響用戶體驗
                            pass

                    # Add messages to session state
                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": user_input,
                            "emotion": emotion,
                            "intent": intent,
                            "timestamp": timestamp,
                        }
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                        }
                    )

                    # Rerun to update chat display
                    st.rerun()

                else:
                    error_msg = ""
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg = error_data["error"]
                    except:
                        error_msg = response.text

                    # 檢查是否是 OpenAI API 配額問題
                    if response.status_code == 429 or "insufficient_quota" in str(
                        error_msg
                    ):
                        st.error("⚠️ OpenAI API 配額已用完")
                        st.warning(
                            "**解決方案：**\n\n"
                            "1. 前往 [OpenAI 帳戶](https://platform.openai.com/account/billing) 充值\n"
                            "2. 或暫時使用規則匹配模式（準確率較低）\n\n"
                            "**目前系統使用規則匹配為您提供基本回答：**"
                        )

                        # 使用簡單的規則匹配作為備用
                        fallback_answer = get_fallback_answer(user_input)
                        st.write(fallback_answer)
                        st.caption(datetime.now().strftime("%H:%M:%S"))

                        # 添加到聊天記錄
                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": user_input,
                                "emotion": "未知",
                                "intent": "未知",
                                "timestamp": timestamp,
                            }
                        )
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": fallback_answer,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "fallback": True,
                            }
                        )
                        st.rerun()
                    else:
                        st.error(f"❌ API 錯誤: {response.status_code}")
                        st.write("抱歉，系統暫時無法回應，請稍後再試。")
                        if error_msg:
                            with st.expander("查看錯誤詳情"):
                                st.code(error_msg)

            except requests.exceptions.Timeout:
                st.error("⏰ 請求超時，請稍後再試")
            except requests.exceptions.ConnectionError:
                st.error("❌ 無法連接到 API 服務，請確認服務是否運行")
            except Exception as e:
                st.error(f"❌ 發生錯誤: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### 💡 快速問題")

    if st.button("⏰ 營業時間", use_container_width=True):
        st.session_state.quick_question = "你們的營業時間是什麼時候？"
        st.rerun()

    if st.button("🚚 運送政策", use_container_width=True):
        st.session_state.quick_question = "請問運送政策是什麼？"
        st.rerun()

    if st.button("↩️ 退換貨", use_container_width=True):
        st.session_state.quick_question = "我想要退換貨，該怎麼辦？"
        st.rerun()

    if st.button("📦 查詢訂單", use_container_width=True):
        st.session_state.quick_question = "我想查詢我的訂單進度"
        st.rerun()

    st.markdown("---")

    if st.button("🗑️ 清除對話記錄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "對話已清除。有什麼可以幫助您的嗎？",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 對話統計")
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.metric("已提問次數", user_messages)

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 10px;'>
    <p>💬 AI 客服聊天助理 | 24/7 全天候服務</p>
</div>
""",
    unsafe_allow_html=True,
)
