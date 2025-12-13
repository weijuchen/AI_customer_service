"""
客戶反饋數據庫 - 簡單的 JSON 存儲
用於存儲和檢索客戶聊天記錄和情緒分析結果
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class CustomerFeedbackDB:
    """客戶反饋數據庫"""
    
    def __init__(self, db_path: str = "customer_feedback.json"):
        self.db_path = db_path
        self.feedbacks = self._load_db()
    
    def _load_db(self) -> List[Dict]:
        """載入數據庫"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_db(self):
        """保存數據庫"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.feedbacks, f, ensure_ascii=False, indent=2)
    
    def add_feedback(self, 
                     user_message: str, 
                     emotion: str, 
                     emotion_confidence: float,
                     intent: str = None,
                     session_id: str = None):
        """添加客戶反饋"""
        feedback = {
            "id": len(self.feedbacks) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "user_message": user_message,
            "emotion": emotion,
            "emotion_confidence": emotion_confidence,
            "intent": intent,
            "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "is_negative": emotion == "負面",
            "needs_attention": emotion == "負面" and emotion_confidence > 0.7
        }
        
        self.feedbacks.append(feedback)
        self._save_db()
        return feedback
    
    def get_all_feedbacks(self, limit: int = None) -> List[Dict]:
        """獲取所有反饋"""
        feedbacks = sorted(self.feedbacks, key=lambda x: x['timestamp'], reverse=True)
        if limit:
            return feedbacks[:limit]
        return feedbacks
    
    def get_negative_feedbacks(self) -> List[Dict]:
        """獲取負面反饋"""
        return [f for f in self.feedbacks if f['is_negative']]
    
    def get_feedbacks_need_attention(self) -> List[Dict]:
        """獲取需要關注的反饋"""
        return [f for f in self.feedbacks if f['needs_attention']]
    
    def get_emotion_stats(self) -> Dict:
        """獲取情緒統計"""
        if not self.feedbacks:
            return {
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "positive_rate": 0,
                "negative_rate": 0
            }
        
        total = len(self.feedbacks)
        positive = len([f for f in self.feedbacks if f['emotion'] == '正面'])
        neutral = len([f for f in self.feedbacks if f['emotion'] == '中性'])
        negative = len([f for f in self.feedbacks if f['emotion'] == '負面'])
        
        return {
            "total": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_rate": positive / total * 100 if total > 0 else 0,
            "negative_rate": negative / total * 100 if total > 0 else 0
        }
    
    def get_today_stats(self) -> Dict:
        """獲取今日統計"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_feedbacks = [f for f in self.feedbacks if f['date'] == today]
        
        if not today_feedbacks:
            return {
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }
        
        return {
            "total": len(today_feedbacks),
            "positive": len([f for f in today_feedbacks if f['emotion'] == '正面']),
            "neutral": len([f for f in today_feedbacks if f['emotion'] == '中性']),
            "negative": len([f for f in today_feedbacks if f['emotion'] == '負面'])
        }
    
    def clear_all(self):
        """清空所有數據"""
        self.feedbacks = []
        self._save_db()


# 全局實例
feedback_db = CustomerFeedbackDB()


if __name__ == "__main__":
    # 測試
    db = CustomerFeedbackDB("test_feedback.json")
    
    # 添加測試數據
    db.add_feedback("產品很好用！", "正面", 0.95, "產品諮詢")
    db.add_feedback("服務態度很差", "負面", 0.88, "投訴建議")
    db.add_feedback("還可以", "中性", 0.75, "其他")
    
    print("所有反饋:", len(db.get_all_feedbacks()))
    print("負面反饋:", len(db.get_negative_feedbacks()))
    print("情緒統計:", db.get_emotion_stats())
    print("今日統計:", db.get_today_stats())


