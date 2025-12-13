"""
Customer Intent Analysis Dashboard - Staff Dashboard (Password Protected)
客戶意圖分析儀表板 - 後台功能（需密碼）
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
    page_title="意圖分析 - 後台",
    page_icon="🎯",
    layout="wide",
)

# ==================== 密碼保護 ====================
st.title("🔒 客戶意圖分析儀表板")

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
    st.markdown("### 🎯 意圖篩選")
    intent_filter = st.selectbox(
        "顯示意圖",
        ["全部意圖", "查詢訂單", "退換貨問題", "物流配送", "產品諮詢", "帳號問題", "投訴建議", "其他"]
    )

st.markdown("分析客戶問題類型與意圖分布")
st.markdown("---")

# 檢查數據庫
if feedback_db is None:
    st.error("❌ 數據庫未初始化")
    st.stop()

# 獲取所有反饋
all_feedbacks = feedback_db.get_all_feedbacks()

if len(all_feedbacks) == 0:
    st.info("📭 目前沒有客戶反饋記錄")
    st.markdown("客戶使用聊天功能後，數據會自動顯示在這裡")
    st.stop()

# ==================== 意圖統計 ====================
st.markdown("## 📊 意圖分布統計")

# 計算意圖分布
intent_counts = {}
for feedback in all_feedbacks:
    intent = feedback.get('intent', '其他')
    intent_counts[intent] = intent_counts.get(intent, 0) + 1

# 排序
sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)

# 顯示統計卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "總問題數",
        len(all_feedbacks),
        delta=f"共 {len(intent_counts)} 種意圖"
    )

with col2:
    if sorted_intents:
        top_intent = sorted_intents[0]
        st.metric(
            "最多問題類型",
            top_intent[0],
            delta=f"{top_intent[1]} 次 ({top_intent[1]/len(all_feedbacks)*100:.1f}%)"
        )

with col3:
    # 計算需要關注的意圖（退換貨、投訴）
    critical_intents = ["退換貨問題", "投訴建議"]
    critical_count = sum([intent_counts.get(i, 0) for i in critical_intents])
    st.metric(
        "需要關注",
        critical_count,
        delta="退換貨+投訴",
        delta_color="inverse" if critical_count > 5 else "normal"
    )

with col4:
    # 今日問題數
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = len([f for f in all_feedbacks if f.get('date') == today])
    st.metric(
        "今日問題",
        today_count,
        delta="今天"
    )

st.markdown("---")

# ==================== 意圖分布圖表 ====================
st.markdown("## 📈 意圖分布圖表")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 意圖數量分布")
    
    # 創建 DataFrame
    intent_df = pd.DataFrame(sorted_intents, columns=['意圖', '數量'])
    
    # 顯示柱狀圖
    st.bar_chart(intent_df.set_index('意圖'))

with col2:
    st.markdown("### 意圖比例")
    
    # 顯示比例
    for intent, count in sorted_intents:
        percentage = count / len(all_feedbacks) * 100
        st.write(f"**{intent}**: {count} 次 ({percentage:.1f}%)")
        st.progress(percentage / 100)

st.markdown("---")

# ==================== 意圖詳細分析 ====================
st.markdown("## 🎯 各意圖詳細分析")

# 意圖圖標配置
intent_config = {
    "查詢訂單": {"emoji": "📦", "color": "#2196F3", "priority": "中"},
    "退換貨問題": {"emoji": "↩️", "color": "#FF9800", "priority": "高"},
    "物流配送": {"emoji": "🚚", "color": "#4CAF50", "priority": "中"},
    "產品諮詢": {"emoji": "🛍️", "color": "#9C27B0", "priority": "低"},
    "帳號問題": {"emoji": "👤", "color": "#F44336", "priority": "中"},
    "投訴建議": {"emoji": "💬", "color": "#FF5722", "priority": "高"},
    "其他": {"emoji": "❓", "color": "#607D8B", "priority": "低"},
}

# 顯示每個意圖的統計卡片
for intent, count in sorted_intents:
    config = intent_config.get(intent, {"emoji": "❓", "color": "#607D8B", "priority": "低"})
    
    with st.expander(
        f"{config['emoji']} {intent} - {count} 次 ({count/len(all_feedbacks)*100:.1f}%)",
        expanded=(count == sorted_intents[0][1])  # 最多的意圖默認展開
    ):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(
                f"<div style='text-align: center; padding: 20px; background-color: {config['color']}; "
                f"color: white; border-radius: 10px;'>"
                f"<h2>{config['emoji']}</h2>"
                f"<h3>{intent}</h3>"
                f"<p>共 {count} 次提問</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with col2:
            st.metric("佔比", f"{count/len(all_feedbacks)*100:.1f}%")
            st.metric("優先級", config['priority'])
        
        with col3:
            # 計算該意圖的情緒分布
            intent_feedbacks = [f for f in all_feedbacks if f.get('intent') == intent]
            positive = len([f for f in intent_feedbacks if f.get('emotion') == '正面'])
            negative = len([f for f in intent_feedbacks if f.get('emotion') == '負面'])
            
            st.metric("正面反饋", positive)
            st.metric("負面反饋", negative)
        
        # 顯示該意圖的最近問題
        st.markdown("#### 最近問題示例")
        recent_feedbacks = [f for f in all_feedbacks if f.get('intent') == intent][:5]
        
        for fb in recent_feedbacks:
            emotion_emoji = {"正面": "😊", "中性": "😐", "負面": "😞"}.get(fb.get('emotion'), "❓")
            st.markdown(
                f"- {emotion_emoji} **{fb.get('timestamp')}**: {fb.get('user_message')}"
            )

st.markdown("---")

# ==================== 客戶問題列表 ====================
st.markdown("## 📋 客戶問題列表")

# 根據篩選獲取反饋
if intent_filter == "全部意圖":
    filtered_feedbacks = all_feedbacks
else:
    filtered_feedbacks = [f for f in all_feedbacks if f.get('intent') == intent_filter]

st.markdown(f"顯示 **{len(filtered_feedbacks)}** 條問題")

# 分頁設定
items_per_page = 10
total_pages = (len(filtered_feedbacks) + items_per_page - 1) // items_per_page

if total_pages > 0:
    page = st.number_input("頁碼", min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_feedbacks = filtered_feedbacks[start_idx:end_idx]
    
    # 顯示問題列表
    for feedback in page_feedbacks:
        intent = feedback.get('intent', '其他')
        config = intent_config.get(intent, {"emoji": "❓", "color": "#607D8B"})
        
        # 情緒配置
        emotion = feedback.get('emotion', '未知')
        if emotion == '正面':
            emotion_color = "#4caf50"
            emotion_emoji = "😊"
        elif emotion == '中性':
            emotion_color = "#ff9800"
            emotion_emoji = "😐"
        else:
            emotion_color = "#f44336"
            emotion_emoji = "😞"
        
        # 顯示問題卡片
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{feedback['timestamp']}**")
                st.markdown(f"{feedback['user_message']}")
            
            with col2:
                st.markdown(
                    f"<div style='text-align: center; padding: 10px; background-color: {config['color']}; "
                    f"color: white; border-radius: 5px;'>"
                    f"{config['emoji']} {intent}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    f"<div style='text-align: center; padding: 10px; background-color: {emotion_color}; "
                    f"color: white; border-radius: 5px;'>"
                    f"{emotion_emoji} {emotion}<br>"
                    f"{feedback.get('emotion_confidence', 0):.0%}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("---")
    
    # 頁碼資訊
    st.caption(f"第 {page} / {total_pages} 頁 | 共 {len(filtered_feedbacks)} 條記錄")

st.markdown("---")

# ==================== 意圖趨勢分析 ====================
st.markdown("## 📉 意圖趨勢分析")

# 按日期統計
date_intent_stats = {}
for feedback in all_feedbacks:
    date = feedback.get('date', 'Unknown')
    intent = feedback.get('intent', '其他')
    
    if date not in date_intent_stats:
        date_intent_stats[date] = {}
    
    date_intent_stats[date][intent] = date_intent_stats[date].get(intent, 0) + 1

# 顯示最近3天的趨勢
if date_intent_stats:
    st.markdown("### 最近日期的意圖分布")
    
    sorted_dates = sorted(date_intent_stats.keys(), reverse=True)[:3]
    
    for date in sorted_dates:
        st.markdown(f"#### {date}")
        
        date_intents = date_intent_stats[date]
        sorted_date_intents = sorted(date_intents.items(), key=lambda x: x[1], reverse=True)
        
        cols = st.columns(len(sorted_date_intents))
        for i, (intent, count) in enumerate(sorted_date_intents):
            with cols[i]:
                config = intent_config.get(intent, {"emoji": "❓", "color": "#607D8B"})
                st.metric(
                    f"{config['emoji']} {intent}",
                    count,
                    delta=f"{count/sum(date_intents.values())*100:.0f}%"
                )

st.markdown("---")

# ==================== 重點關注區域 ====================
st.markdown("## ⚠️ 需要重點關注的意圖")

critical_intents_data = []
for intent in ["退換貨問題", "投訴建議", "帳號問題"]:
    count = intent_counts.get(intent, 0)
    if count > 0:
        critical_intents_data.append({
            "意圖": intent,
            "數量": count,
            "佔比": f"{count/len(all_feedbacks)*100:.1f}%"
        })

if critical_intents_data:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 關鍵意圖統計")
        for item in critical_intents_data:
            config = intent_config.get(item['意圖'], {"emoji": "❓", "color": "#607D8B"})
            st.markdown(
                f"**{config['emoji']} {item['意圖']}**: {item['數量']} 次 ({item['佔比']})"
            )
    
    with col2:
        st.markdown("### 建議行動")
        if intent_counts.get("退換貨問題", 0) > 5:
            st.warning("⚠️ 退換貨問題較多，建議檢查產品質量")
        if intent_counts.get("投訴建議", 0) > 3:
            st.error("🚨 投訴較多，需要立即處理")
        if intent_counts.get("帳號問題", 0) > 5:
            st.info("💡 帳號問題頻繁，考慮優化帳號系統")
else:
    st.success("✅ 目前沒有需要特別關注的問題")

st.markdown("---")

# ==================== 管理功能 ====================
st.markdown("## 🛠️ 管理功能")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 匯出意圖數據", use_container_width=True):
        # 創建意圖統計數據
        export_data = {
            "總計": len(all_feedbacks),
            "意圖分布": intent_counts,
            "生成時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.download_button(
            label="下載 JSON",
            data=str(export_data),
            file_name=f"intent_analysis_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

with col2:
    if st.button("📊 生成意圖報告", use_container_width=True):
        st.info("意圖報告生成功能開發中...")

with col3:
    if st.button("🔄 重新統計", use_container_width=True):
        st.rerun()

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
    <p>🎯 客戶意圖分析儀表板 | 僅供內部使用</p>
</div>
""",
    unsafe_allow_html=True,
)
