"""
AI Customer Service Smart Analysis System - Streamlit Frontend Interface
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Customer Service Analysis System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API URL from environment variable, defaults to localhost
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS styles
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Main title
st.markdown(
    '<h1 class="main-header">🤖 AI Customer Service Smart Analysis System</h1>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 System Features")
    page = st.radio(
        "Select Function Module:",
        ["🏠 Home", "😊 Emotion Analysis", "🤖 Smart Q&A", "📈 System Monitor"],
    )

    st.markdown("---")
    st.markdown("### ⚙️ System Status")

    # Check API health status
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        if response.status_code == 200:
            st.success("✅ API Service is Running")
            health_data = response.json()
            with st.expander("View Details"):
                st.json(health_data)
        else:
            st.error("❌ API Service is Abnormal")
    except Exception as e:
        st.error(f"❌ Cannot connect to API\n{str(e)}")

    st.markdown("---")
    st.markdown("### 📝 Technology Stack")
    st.info(
        """
    **Deep Learning**
    - PyTorch (TextCNN)
    - BERT (Intent Recognition)
    
    **Backend**
    - FastAPI
    - OpenAI API
    
    **Deployment**
    - Docker
    - Docker Compose
    """
    )

# ==================== Home Page ====================
if page == "🏠 Home":
    st.markdown("## Welcome to the AI Customer Service Smart Analysis System")

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h2>😊</h2>
            <h3>Emotion Analysis</h3>
            <p>TextCNN Deep Learning Model</p>
            <h4>Accuracy 95%+</h4>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h2>🎯</h2>
            <h3>Intent Recognition</h3>
            <p>BERT Pre-trained Model</p>
            <h4>Multi-class Classification</h4>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h2>🤖</h2>
            <h3>Smart Q&A</h3>
            <p>RAG + LLM</p>
            <h4>Instant Response</h4>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # System Architecture
    st.markdown("## 🏗️ System Architecture")
    st.code(
        """
    ┌──────────────────────────────────────────────────────┐
    │          Streamlit Frontend Interface (Port 8501)    │
    └──────────────────────────────────────────────────────┘
                              ↓ HTTP Request
    ┌──────────────────────────────────────────────────────┐
    │          FastAPI Backend Service (Port 8000)         │
    │  ┌────────────────┐  ┌────────────────┐              │
    │  │ Emotion Module │  │ Intent Module  │              │
    │  │  (TextCNN)     │  │    (BERT)      │              │
    │  └────────────────┘  └────────────────┘              │
    │  ┌────────────────────────────────────┐              │
    │  │ Smart Q&A Module (RAG + OpenAI)    │              │
    │  └────────────────────────────────────┘              │
    └──────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────────────────────────────────────────┐
    │                Docker Container Orchestration        │
    │         (docker-compose manages multiple containers) │
    └──────────────────────────────────────────────────────┘
    """,
        language="text",
    )

    st.markdown("---")

    # Quick Start
    st.markdown("## 🚀 Quick Start")
    st.info("👈 Please select a function from the left menu to test")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Emotion Analysis")
        st.write(
            "Input customer feedback text, and the system will automatically analyze the emotional tendency."
        )
    with col2:
        st.markdown("### 🤖 Smart Q&A")
        st.write(
            "Ask common questions, and the system will retrieve and generate answers from the knowledge base."
        )

# ==================== Emotion Analysis ====================
elif page == "😊 Emotion Analysis":
    st.markdown("## 😊 Customer Emotion Analysis")
    st.markdown("---")

    # Input area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 Input Text")
        user_text = st.text_area(
            "Please enter customer feedback:",
            height=150,
            placeholder="e.g., The quality of your product is great, and the customer service attitude is wonderful!",
        )

    with col2:
        st.markdown("### 💡 Example Texts")
        st.caption("Click to use examples")

        if st.button("😊 Positive Example", use_container_width=True):
            user_text = "The product quality is excellent, the customer service attitude is great, and the logistics are fast!"
            st.rerun()

        if st.button("😐 Neutral Example", use_container_width=True):
            user_text = "Product received, currently using, no strong feelings yet."
            st.rerun()

        if st.button("😞 Negative Example", use_container_width=True):
            user_text = "The product quality is too poor, the customer service attitude is bad, and I waited a long time for a reply."
            st.rerun()

    st.markdown("---")

    # Analysis button
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        if not user_text or len(user_text.strip()) == 0:
            st.warning("⚠️ Please enter text first")
        else:
            with st.spinner("🔄 Analyzing..."):
                try:
                    # Call API
                    response = requests.post(
                        f"{API_URL}/analyze", json={"text": user_text}, timeout=10
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.success("✅ Analysis Complete!")
                        st.markdown("---")

                        # Display results
                        st.markdown("### 📊 Analysis Results")

                        # Emotion label and color configuration
                        emotion_config = {
                            "positive": {
                                "emoji": "😊",
                                "label": "Positive",
                                "color": "#28a745",
                            },
                            "neutral": {
                                "emoji": "😐",
                                "label": "Neutral",
                                "color": "#ffc107",
                            },
                            "negative": {
                                "emoji": "😞",
                                "label": "Negative",
                                "color": "#dc3545",
                            },
                        }

                        emotion = result.get("emotion", "unknown")
                        config = emotion_config.get(
                            emotion,
                            {"emoji": "🤔", "label": "Unknown", "color": "#6c757d"},
                        )

                        # Main result card
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(
                                f"""
                            <div style='text-align: center; padding: 30px; 
                                        background-color: {config['color']}; 
                                        border-radius: 15px; color: white;'>
                                <div style='font-size: 4rem;'>{config['emoji']}</div>
                                <h2>{config['label']}</h2>
                                <p style='font-size: 1.2rem;'>Emotion Category</p>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col2:
                            confidence = result.get("confidence", 0)
                            st.metric(
                                label="Confidence",
                                value=f"{confidence:.2%}",
                                delta=(
                                    "High Confidence"
                                    if confidence > 0.8
                                    else "Moderate Confidence"
                                ),
                            )

                        with col3:
                            probs = result.get("probabilities", {})
                            sentiment_score = probs.get("positive", 0) - probs.get(
                                "negative", 0
                            )
                            st.metric(
                                label="Sentiment Score",
                                value=f"{sentiment_score:.3f}",
                                delta="Positive" if sentiment_score > 0 else "Negative",
                            )

                        st.markdown("---")

                        # Detailed probability distribution
                        st.markdown("#### 📈 Probability Distribution by Category")

                        probs = result.get("probabilities", {})
                        for label, prob in probs.items():
                            col_label, col_bar = st.columns([1, 4])
                            with col_label:
                                st.write(f"**{label.capitalize()}**")
                            with col_bar:
                                st.progress(prob, text=f"{prob:.2%}")

                        # Raw JSON result
                        with st.expander("🔍 View Full JSON Result"):
                            st.json(result)

                        # Timestamp
                        st.caption(
                            f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )

                    else:
                        st.error(f"❌ API returned an error: {response.status_code}")
                        st.code(response.text)

                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out, please try again later")
                except requests.exceptions.ConnectionError:
                    st.error(
                        "❌ Cannot connect to API service, please check if the service is running"
                    )
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# ==================== Smart Q&A ====================
elif page == "🤖 Smart Q&A":
    st.markdown("## 🤖 Smart Q&A System")
    st.markdown("Based on RAG (Retrieval-Augmented Generation) + LLM")
    st.markdown("---")

    # Input question
    user_question = st.text_input(
        "Please enter your question:", placeholder="e.g., What are your business hours?"
    )

    # Quick access for common questions
    st.markdown("### 💡 Common Questions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⏰ Business Hours", use_container_width=True):
            user_question = "What time are your business hours?"
            st.rerun()

    with col2:
        if st.button("🚚 Shipping Policy", use_container_width=True):
            user_question = "What is your shipping policy?"
            st.rerun()

    with col3:
        if st.button("↩️ Return Policy", use_container_width=True):
            user_question = "How do I request a return or exchange?"
            st.rerun()

    st.markdown("---")

    # Submit button
    if st.button("💬 Get Answer", type="primary", use_container_width=True):
        if not user_question or len(user_question.strip()) == 0:
            st.warning("⚠️ Please enter a question first")
        else:
            with st.spinner("🤖 AI is thinking..."):
                try:
                    # Call Q&A API
                    response = requests.post(
                        f"{API_URL}/qa", json={"question": user_question}, timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.success("✅ Answer generation complete!")
                        st.markdown("---")

                        # Display answer
                        st.markdown("### 💬 AI Answer")
                        answer = result.get("answer", "Unable to generate an answer")
                        st.markdown(
                            f"""
                            <div style='background-color: #f0f2f6; padding: 20px; 
                                        border-radius: 10px; border-left: 5px solid #1f77b4;'>
                                {answer}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Relevant sources
                        if "sources" in result:
                            st.markdown("---")
                            st.markdown("### 📚 Reference Sources")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(f"Source {i}"):
                                    st.write(source)

                        # Full result
                        with st.expander("🔍 View Full Result"):
                            st.json(result)

                    else:
                        st.error(f"❌ API returned an error: {response.status_code}")

                except requests.exceptions.Timeout:
                    st.error(
                        "⏰ Request timed out (LLM generation can be slow), please try again later"
                    )
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# ==================== System Monitor ====================
elif page == "📈 System Monitor":
    st.markdown("## 📈 System Monitoring Dashboard")
    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()

    # Get health status
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()

            # System status cards
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Service Status", "🟢 Running")

            with col2:
                st.metric("API Port", "8000")

            with col3:
                st.metric("Response Time", f"{response.elapsed.total_seconds():.3f}s")

            st.markdown("---")

            # Detailed information
            st.markdown("### 📋 Detailed Information")
            st.json(health_data)

        else:
            st.error("❌ Service is Abnormal")

    except Exception as e:
        st.error(f"❌ Cannot connect to service: {str(e)}")

    st.markdown("---")

    # Docker Information
    st.markdown("### 🐳 Docker Deployment Information")
    st.info(
        """
    **Container Services**
    - API Container: ai-customer-service-api (Port 8000)
    - Frontend Container: ai-customer-service-frontend (Port 8501)
    
    **Network**
    - Network Name: ai-network
    - Driver Type: bridge
    
    **Health Check**
    - Interval: 30s
    - Timeout: 10s
    - Retries: 3
    """
    )

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>AI Customer Service Smart Analysis System | Powered by PyTorch + FastAPI + Docker</p>
    <p>© 2025 | Day 3 Demo Project</p>
</div>
""",
    unsafe_allow_html=True,
)
