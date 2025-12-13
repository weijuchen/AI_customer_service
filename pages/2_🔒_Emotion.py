"""
Customer Feedback Monitoring Dashboard - Staff Dashboard (Password Protected)
客戶反饋監控儀表板 - 後台功能（需密碼）
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import feedback database
try:
    from customer_feedback_db import feedback_db
except:
    st.error("無法載入客戶反饋數據庫")
    feedback_db = None

# Page configuration
st.set_page_config(
    page_title="客戶反饋監控 - 後台",
    page_icon="📊",
    layout="wide",
)

# ==================== 密碼保護 ====================
st.title("🔒 客戶反饋監控儀表板")

# Password protection
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.warning("⚠️ 此頁面需要管理員權限")
    password = st.text_input("請輸入管理密碼", type="password", key="password_input")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("登入", type="primary", use_container_width=True):
            if password == st.secrets.get("ADMIN_PASSWORD", ""):
                st.session_state.authenticated = True
                st.success("✅ 登入成功！")
                st.rerun()
            else:
                st.error("❌ 密碼錯誤")

    with col2:
        if st.button("返回首頁", use_container_width=True):
            st.switch_page("streamlit_app.py")

    st.stop()

# ==================== 已認證，顯示儀表板 ====================

# Logout button in sidebar
with st.sidebar:

    st.markdown("### 🧭 常用功能")
    if st.button("🏠 返回首頁  ", use_container_width=True):
        st.switch_page("streamlit_app.py")
    st.markdown("---")

    st.markdown("### 👤 管理員已登入")
    if st.button("🚪 登出", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔄 刷新設定")
    auto_refresh = st.checkbox("自動刷新 (30秒)", value=False)

    if st.button("🔄 立即刷新", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 篩選選項")
    filter_option = st.selectbox(
        "顯示反饋", ["全部反饋", "僅負面反饋", "需要關注", "今日反饋"]
    )

st.markdown("即時監控客戶反饋與情緒分析")
st.markdown("---")

# 檢查數據庫
if feedback_db is None:
    st.error("❌ 數據庫未初始化")
    st.stop()

# 獲取統計數據
stats = feedback_db.get_emotion_stats()
today_stats = feedback_db.get_today_stats()
all_feedbacks = feedback_db.get_all_feedbacks()

# ==================== 統計卡片 ====================
st.markdown("## 📈 整體統計")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("總反饋數", stats["total"], delta=f"今日 +{today_stats['total']}")

with col2:
    positive_rate = stats["positive_rate"]
    st.metric(
        "正面反饋",
        f"{stats['positive']} ({positive_rate:.1f}%)",
        delta="健康" if positive_rate > 70 else "需改善",
        delta_color="normal" if positive_rate > 70 else "inverse",
    )

with col3:
    negative_rate = stats["negative_rate"]
    st.metric(
        "負面反饋",
        f"{stats['negative']} ({negative_rate:.1f}%)",
        delta="警告" if negative_rate > 20 else "正常",
        delta_color="inverse" if negative_rate > 20 else "normal",
    )

with col4:
    needs_attention = len(feedback_db.get_feedbacks_need_attention())
    st.metric(
        "需要關注",
        needs_attention,
        delta="緊急" if needs_attention > 5 else "可控",
        delta_color="inverse" if needs_attention > 5 else "normal",
    )

st.markdown("---")

# ==================== 今日統計 ====================
st.markdown("## 📅 今日統計")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("今日總數", today_stats["total"])
with col2:
    st.metric("今日正面", today_stats["positive"], delta="😊")
with col3:
    st.metric("今日中性", today_stats["neutral"], delta="😐")
with col4:
    st.metric("今日負面", today_stats["negative"], delta="😞")

st.markdown("---")

# ==================== 負面反饋警示 ====================
negative_feedbacks = feedback_db.get_negative_feedbacks()
needs_attention_feedbacks = feedback_db.get_feedbacks_need_attention()

if needs_attention_feedbacks:
    st.markdown("## ⚠️ 需要立即關注的反饋")

    for feedback in needs_attention_feedbacks[:5]:  # 只顯示前5個
        with st.expander(
            f"🚨 {feedback['timestamp']} - 信心度: {feedback['emotion_confidence']:.0%}",
            expanded=True,
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**客戶訊息**: {feedback['user_message']}")
                st.markdown(f"**意圖**: {feedback.get('intent', '未知')}")

            with col2:
                st.markdown(f"**情緒**: 😞 負面")
                st.markdown(f"**信心度**: {feedback['emotion_confidence']:.0%}")
                st.markdown(f"**Session**: {feedback.get('session_id', 'N/A')[:15]}...")

st.markdown("---")

# ==================== 反饋列表 ====================
st.markdown("## 📋 客戶反饋列表")

# 根據篩選選項獲取反饋
if filter_option == "僅負面反饋":
    filtered_feedbacks = negative_feedbacks
elif filter_option == "需要關注":
    filtered_feedbacks = needs_attention_feedbacks
elif filter_option == "今日反饋":
    today = datetime.now().strftime("%Y-%m-%d")
    filtered_feedbacks = [f for f in all_feedbacks if f["date"] == today]
else:
    filtered_feedbacks = all_feedbacks

st.markdown(f"顯示 **{len(filtered_feedbacks)}** 條反饋")

# 分頁設定
items_per_page = 10
total_pages = (len(filtered_feedbacks) + items_per_page - 1) // items_per_page

if total_pages > 0:
    page = st.number_input("頁碼", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_feedbacks = filtered_feedbacks[start_idx:end_idx]

    # 顯示反饋
    for feedback in page_feedbacks:
        # 根據情緒設定顏色
        if feedback["emotion"] == "正面":
            emotion_color = "#4caf50"
            emotion_emoji = "😊"
        elif feedback["emotion"] == "中性":
            emotion_color = "#ff9800"
            emotion_emoji = "😐"
        else:
            emotion_color = "#f44336"
            emotion_emoji = "😞"

        # 顯示反饋卡片
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{feedback['timestamp']}**")
                st.markdown(f"{feedback['user_message']}")

            with col2:
                st.markdown(
                    f"<div style='text-align: center; padding: 10px; background-color: {emotion_color}; "
                    f"color: white; border-radius: 5px;'>"
                    f"{emotion_emoji} {feedback['emotion']}<br>"
                    f"{feedback['emotion_confidence']:.0%}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(f"**意圖**")
                st.markdown(f"{feedback.get('intent', '未知')}")

            st.markdown("---")

    # 頁碼資訊
    st.caption(f"第 {page} / {total_pages} 頁 | 共 {len(filtered_feedbacks)} 條記錄")

else:
    st.info("📭 目前沒有客戶反饋記錄")
    st.markdown("客戶使用聊天功能後，反饋會自動顯示在這裡")

# ==================== 情緒分布圖表 ====================
if len(all_feedbacks) > 0:
    st.markdown("---")
    st.markdown("## 📊 情緒分布")

    # 創建 DataFrame
    df = pd.DataFrame(all_feedbacks)

    # 情緒分布
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 情緒類別分布")
        emotion_counts = df["emotion"].value_counts()
        st.bar_chart(emotion_counts)

    with col2:
        st.markdown("### 情緒比例")
        st.write(f"😊 正面: {stats['positive']} ({stats['positive_rate']:.1f}%)")
        st.write(
            f"😐 中性: {stats['neutral']} ({(stats['neutral']/stats['total']*100):.1f}%)"
        )
        st.write(f"😞 負面: {stats['negative']} ({stats['negative_rate']:.1f}%)")

        # 進度條
        st.progress(
            stats["positive_rate"] / 100, text=f"正面率: {stats['positive_rate']:.1f}%"
        )
        st.progress(
            stats["negative_rate"] / 100, text=f"負面率: {stats['negative_rate']:.1f}%"
        )

# ==================== 管理功能 ====================
st.markdown("---")
st.markdown("## 🛠️ 管理功能")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 匯出數據 (JSON)", use_container_width=True):
        st.download_button(
            label="下載 JSON",
            data=str(all_feedbacks),
            file_name=f"customer_feedback_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )

with col2:
    if st.button("📊 生成報告", use_container_width=True):
        st.info("報告生成功能開發中...")

with col3:
    if st.button("🗑️ 清空所有數據", use_container_width=True, type="secondary"):
        if st.session_state.get("confirm_clear", False):
            feedback_db.clear_all()
            st.success("✅ 數據已清空")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("⚠️ 再次點擊確認清空")

# Auto refresh
if auto_refresh:
    import time

    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 10px;'>
    <p>📊 客戶反饋監控儀表板 | 僅供內部使用</p>
</div>
""",
    unsafe_allow_html=True,
)
