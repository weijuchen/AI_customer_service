"""
AI Customer Service Smart Analysis System - Main Entry Page
主入口頁面
"""

import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(
    page_title="AI 客服智能分析系統",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API URL from environment variable, defaults to localhost
# API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# Custom CSS styles
st.markdown(
    """
<style>
    /* 主標題樣式 */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 0;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .hero-description {
        font-size: 1.2rem;
        opacity: 0.9;
        line-height: 1.8;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* 統計數字 */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        font-size: 1rem;
    }
    
    /* 技術標籤 */
    .tech-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 分隔線 */
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 3rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid #eee;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar - 自定義導航（保持不變）
with st.sidebar:
    st.markdown("### 📊 導航選單")

    # 使用者功能區
    st.markdown("#### 👥 使用者功能")
    if st.button("🏠 首頁", use_container_width=True, key="nav_home"):
        st.switch_page("streamlit_app.py")
    if st.button("💬 聊天助理", use_container_width=True, key="nav_chat"):
        st.switch_page("pages/1_💬_Chat.py")

    st.markdown("---")

    # 公司後台區
    st.markdown("#### 🔐 公司後台")
    if st.button("🔒 情緒分析", use_container_width=True, key="nav_emotion"):
        st.switch_page("pages/2_🔒_Emotion.py")
    if st.button("🔒 意圖識別", use_container_width=True, key="nav_intent"):
        st.switch_page("pages/3_🔒_Intent.py")
    if st.button("🔒 系統監控", use_container_width=True, key="nav_monitoring"):
        st.switch_page("pages/4_🔒_Monitoring.py")

    st.markdown("---")
    st.markdown("### ⚙️ 系統狀態")

    # Check API health status
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        if response.status_code == 200:
            
            st.success("✅ API 服務運行中")
        else:
            st.error("❌ API 服務異常")
    except Exception as e:
        st.error(f"❌ 無法連接 API")

    st.markdown("---")
    st.markdown("### 📝 技術棧")
    st.info(
        """
    **深度學習**
    - PyTorch (TextCNN)
    - BERT (意圖識別)
    
    **後端**
    - FastAPI
    - OpenAI API
    """
    )

# ==================== 首頁內容 ====================

# Main Header
st.markdown(
    '<h1 class="main-header">🤖 AI 客服智能分析系統</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">結合深度學習與自然語言處理，提供智能化客戶服務解決方案</p>',
    unsafe_allow_html=True,
)

# Hero Section
st.markdown(
    """
<div class="hero-section">
    <div class="hero-title">🚀 智能客服，即刻體驗</div>
    <div class="hero-description">
        運用最先進的 AI 技術，為您的客戶提供 24/7 全天候智能服務<br>
        自動分析情緒、識別意圖、智能問答，讓客服工作更輕鬆高效
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Platform Statistics
st.markdown(
    """
<div class="stats-container">
    <div class="stat-item">
        <div class="stat-number">95%+</div>
        <div class="stat-label">情緒識別準確率</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">24/7</div>
        <div class="stat-label">全天候服務</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">7種</div>
        <div class="stat-label">意圖分類</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">即時</div>
        <div class="stat-label">智能回應</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Section Divider
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==================== 核心功能介紹 ====================
st.markdown("## 🎯 核心功能")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">💬</div>
    <div class="feature-title">智能對話</div>
    <div class="feature-description">
        基於 RAG 架構的智能問答系統<br>
        結合 FAISS 向量檢索與 GPT-4o-mini<br>
        提供準確、自然的對話體驗
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">😊</div>
    <div class="feature-title">情緒分析</div>
    <div class="feature-description">
        TextCNN 深度學習模型<br>
        自動識別客戶情緒（正面/中性/負面）<br>
        準確率高達 95% 以上
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">🎯</div>
    <div class="feature-title">意圖識別</div>
    <div class="feature-description">
        BERT 預訓練模型<br>
        自動分類客戶問題類型<br>
        支援 7 種意圖分類
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">📊</div>
    <div class="feature-title">數據監控</div>
    <div class="feature-description">
        即時監控客戶反饋<br>
        自動識別負面情緒<br>
        提供視覺化儀表板
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">🔍</div>
    <div class="feature-title">智能檢索</div>
    <div class="feature-description">
        FAISS 向量資料庫<br>
        快速檢索相關問答<br>
        提高回應準確性
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">🔒</div>
    <div class="feature-title">安全管理</div>
    <div class="feature-description">
        後台功能密碼保護<br>
        數據安全加密<br>
        權限分級管理
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

# Section Divider
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==================== 使用者功能 ====================
# st.markdown("## 👥 使用者功能")
# st.markdown("### 公開使用，無需密碼")

# col1, col2 = st.columns(2)

# with col1:
#     st.markdown(
#         """
# <div class="feature-card">
#     <div class="feature-icon">💬</div>
#     <div class="feature-title">AI 聊天助理</div>
#     <div class="feature-description">
#         • 24/7 全天候智能客服<br>
#         • 自動情緒與意圖分析<br>
#         • 快速問題一鍵發送<br>
#         • 對話記錄自動保存<br>
#         • 支援規則匹配備用模式
#     </div>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     if st.button(
#         "🚀 開始對話", use_container_width=True, type="primary", key="start_chat"
#     ):
#         st.switch_page("pages/1_💬_Chat.py")

# with col2:
#     st.markdown(
#         """
# <div class="feature-card">
#     <div class="feature-icon">📚</div>
#     <div class="feature-title">智能知識庫</div>
#     <div class="feature-description">
#         • 常見問題快速查詢<br>
#         • 向量檢索精準匹配<br>
#         • 自動推薦相關問答<br>
#         • 持續學習優化<br>
#         • 多語言支援（開發中）
#     </div>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     st.button("📖 瀏覽知識庫", use_container_width=True, disabled=True, key="kb")

# # Section Divider
# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==================== 後台功能 ====================
# st.markdown("## 🔐 公司後台功能")
# st.markdown("### 需要管理員密碼")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown(
#         """
# <div class="feature-card">
#     <div class="feature-icon">😊</div>
#     <div class="feature-title">客戶反饋監控</div>
#     <div class="feature-description">
#         • 即時情緒分析<br>
#         • 負面反饋自動提醒<br>
#         • 情緒趨勢圖表<br>
#         • 需要關注客戶標記<br>
#         • 數據匯出功能
#     </div>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     if st.button("進入 →", key="emotion_btn", use_container_width=True):
#         st.switch_page("pages/2_🔒_Emotion.py")

# with col2:
#     st.markdown(
#         """
# <div class="feature-card">
#     <div class="feature-icon">🎯</div>
#     <div class="feature-title">客戶意圖分析</div>
#     <div class="feature-description">
#         • 問題類型統計<br>
#         • 意圖分布圖表<br>
#         • 重點問題識別<br>
#         • 趨勢分析報告<br>
#         • 客服資源優化建議
#     </div>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     if st.button("進入 →", key="intent_btn", use_container_width=True):
#         st.switch_page("pages/3_🔒_Intent.py")

# with col3:
#     st.markdown(
#         """
# <div class="feature-card">
#     <div class="feature-icon">📈</div>
#     <div class="feature-title">系統監控</div>
#     <div class="feature-description">
#         • API 服務狀態<br>
#         • 模型運行監控<br>
#         • 性能指標追蹤<br>
#         • 錯誤日誌記錄<br>
#         • 系統健康檢查
#     </div>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     if st.button("進入 →", key="monitoring_btn", use_container_width=True):
#         st.switch_page("pages/4_🔒_Monitoring.py")

# # Section Divider
# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==================== 技術架構 ====================
# st.markdown("## 🏗️ 技術架構")

# col1, col2 = st.columns(2)

# with col1:
#     st.markdown("### 🎨 前端技術")
#     st.markdown(
#         """
# <div style="padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
#     <span class="tech-badge">Streamlit</span>
#     <span class="tech-badge">Python</span>
#     <span class="tech-badge">HTML/CSS</span>
#     <span class="tech-badge">JavaScript</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("### 🤖 AI 模型")
#     st.markdown(
#         """
# <div style="padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
#     <span class="tech-badge">PyTorch</span>
#     <span class="tech-badge">TextCNN</span>
#     <span class="tech-badge">BERT</span>
#     <span class="tech-badge">GPT-4o-mini</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )

# with col2:
#     st.markdown("### ⚙️ 後端技術")
#     st.markdown(
#         """
# <div style="padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
#     <span class="tech-badge">FastAPI</span>
#     <span class="tech-badge">OpenAI API</span>
#     <span class="tech-badge">FAISS</span>
#     <span class="tech-badge">Docker</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("### 📦 部署方式")
#     st.markdown(
#         """
# <div style="padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
#     <span class="tech-badge">Docker Compose</span>
#     <span class="tech-badge">Microservices</span>
#     <span class="tech-badge">RESTful API</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )

# # Section Divider
# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# # ==================== 快速開始 ====================
# st.markdown("## 🚀 快速開始")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("### 1️⃣ 體驗聊天")
#     st.info("點擊「開始對話」按鈕，立即與 AI 客服對話")

# with col2:
#     st.markdown("### 2️⃣ 查看分析")
#     st.info("輸入密碼進入後台，查看客戶反饋分析")

# with col3:
#     st.markdown("### 3️⃣ 監控數據")
#     st.info("使用儀表板即時監控客戶情緒與意圖")

# # Footer
# st.markdown(
#     """
# <div class="footer">
#     <h3>🤖 AI 客服智能分析系統</h3>
#     <p>Powered by PyTorch + BERT + FastAPI + OpenAI + Docker</p>
#     <p>© 2025 | 使用者功能公開 | 後台功能需密碼</p>
#     <p style="margin-top: 1rem; color: #999;">
#         結合深度學習、自然語言處理與雲端技術，打造智能化客戶服務解決方案
#     </p>
# </div>
# """,
#     unsafe_allow_html=True,
# )
