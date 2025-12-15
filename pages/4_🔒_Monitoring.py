"""
System Monitoring Page - Staff Dashboard (Password Protected)
系統監控頁面 - 後台功能（需密碼）
"""

import streamlit as st
import requests
import os
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="系統監控 - 後台",
    page_icon="📈",
    layout="wide",
)

# ==================== 密碼保護 ====================
st.title("🔒 系統監控 - 後台功能")

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

# ==================== 已認證，顯示功能 ====================

# API URL
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.markdown("## 📈 系統監控儀表板")
st.markdown("即時監控系統狀態與服務健康度")
st.markdown("---")

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
    st.markdown("### ⚙️ 自動刷新")
    auto_refresh = st.checkbox("啟用自動刷新 (30秒)", value=False)
    
    if auto_refresh:
        st.info("頁面將每 30 秒自動刷新")
    
    st.markdown("---")
    
    if st.button("🔄 立即刷新", use_container_width=True):
        st.rerun()

# Refresh button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 刷新狀態", use_container_width=True, type="primary"):
        st.rerun()

with col2:
    st.metric("當前時間", datetime.now().strftime("%H:%M:%S"))

st.markdown("---")

# Get health status
try:
    start_time = time.time()
    response = requests.get(f"{API_URL}/", timeout=5)
    response_time = time.time() - start_time
    
    if response.status_code == 200:
        health_data = response.json()

        # System status cards
        st.markdown("### 🟢 服務狀態")
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("服務狀態", "🟢 運行中", delta="正常")

        with col2:
            st.metric("API 端口", "8000")

        with col3:
            st.metric("響應時間", f"{response_time:.3f}s", 
                     delta="快速" if response_time < 0.5 else "正常")

        with col4:
            version = health_data.get("version", "N/A")
            st.metric("版本", version)

        st.markdown("---")

        # Module status
        st.markdown("### 📦 模組狀態")
        
        modules = health_data.get("modules", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        module_list = [
            ("whisper", "🎤 語音轉文字", col1),
            ("emotion", "😊 情緒分析", col2),
            ("intent", "🎯 意圖識別", col3),
            ("rag", "🤖 智能問答", col4),
        ]
        
        for key, label, col in module_list:
            with col:
                status = modules.get(key, "unknown")
                if status == "ready":
                    st.success(f"{label}\n✅ 就緒")
                else:
                    st.error(f"{label}\n❌ 異常")

        st.markdown("---")

        # Detailed information
        st.markdown("### 📋 詳細資訊")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 系統配置")
            st.json({
                "status": health_data.get("status", "N/A"),
                "version": health_data.get("version", "N/A"),
                "response_time": f"{response_time:.3f}s",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        with col2:
            st.markdown("#### 📊 模組狀態")
            st.json(modules)

        # Full health data
        with st.expander("🔍 查看完整健康檢查數據"):
            st.json(health_data)

    else:
        st.error("❌ 服務異常")
        st.metric("HTTP 狀態碼", response.status_code)

except requests.exceptions.Timeout:
    st.error("⏰ 連接超時")
    st.warning("API 服務可能未啟動或響應緩慢")
    
except requests.exceptions.ConnectionError:
    st.error("❌ 無法連接到服務")
    st.warning("請確認 API 服務是否正在運行")
    
except Exception as e:
    st.error(f"❌ 發生錯誤: {str(e)}")

st.markdown("---")

# Docker Information
st.markdown("### 🐳 Docker 部署資訊")

col1, col2 = st.columns(2)

with col1:
    st.info(
        """
    **容器服務**
    - API 容器: ai-customer-service-api
    - 前端容器: ai-customer-service-frontend
    
    **端口配置**
    - API: 8000
    - Frontend: 8501
    """
    )

with col2:
    st.info(
        """
    **網路配置**
    - 網路名稱: ai-network
    - 驅動類型: bridge
    
    **健康檢查**
    - 間隔: 30s
    - 超時: 10s
    - 重試: 3次
    """
    )

st.markdown("---")

# Performance metrics (example data)
st.markdown("### 📊 性能指標")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("今日請求數", "1,234", delta="↑ 15%")

with col2:
    st.metric("平均響應時間", "0.25s", delta="↓ 0.05s")

with col3:
    st.metric("成功率", "99.5%", delta="↑ 0.3%")

with col4:
    st.metric("錯誤數", "6", delta="↓ 2")

st.caption("*示例數據，僅供參考")

st.markdown("---")

# System logs
st.markdown("### 📝 系統日誌")

with st.expander("查看最近日誌"):
    st.code(
        """
[2025-12-08 14:30:15] INFO - API 服務啟動成功
[2025-12-08 14:30:16] INFO - 載入情緒分析模型完成
[2025-12-08 14:30:17] INFO - 載入意圖識別模型完成
[2025-12-08 14:30:18] INFO - RAG 系統初始化完成
[2025-12-08 14:30:19] INFO - 所有模組就緒
[2025-12-08 14:35:22] INFO - 收到分析請求 - 情緒: 正面
[2025-12-08 14:36:45] INFO - 收到聊天請求 - 意圖: 查詢訂單
[2025-12-08 14:38:12] INFO - 收到分析請求 - 情緒: 負面
        """,
        language="log"
    )

# Auto refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 10px;'>
    <p>📈 系統監控儀表板 | 僅供內部使用</p>
</div>
""",
    unsafe_allow_html=True,
)

