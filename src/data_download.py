import pandas as pd
import os

# Create example data (should be replaced with real data in a practical application)
data = {
    "text": [
        # Positive emotion examples
        "非常感謝您的幫助，問題解決了！",
        "服務態度很好，很滿意",
        "太棒了，謝謝你們",
        "效率很高，讚！",
        "產品質量很好，會推薦給朋友",
        "客服人員很專業，解決了我的問題",
        "配送速度很快，很滿意這次購物",
        "超出預期，五星好評",
        # Negative emotion examples
        "這什麼爛服務，太差了",
        "等了好久都沒人理我",
        "產品有問題，要求退款",
        "非常不滿意，態度惡劣",
        "完全沒有解決我的問題",
        "浪費我的時間",
        "品質太差了，不會再買",
        "客服根本不專業",
        # Neutral emotion examples
        "請問訂單編號是多少",
        "我想查詢一下物流資訊",
        "這個產品有什麼顏色",
        "可以幫我確認一下訂單嗎",
        "請告訴我退貨流程",
        "想了解一下產品規格",
        "什麼時候可以收到貨",
        "需要提供什麼資料",
    ],
    "label": [
        # Positive = 2
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        # Negative = 0
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        # Neutral = 1
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ],
}

df = pd.DataFrame(data)

# Save the data

# Note: Using "../data/emotion_data.csv" for relative path consistency
df.to_csv("../data/emotion_data.csv", index=False, encoding="utf-8-sig")
# df.to_csv("data/emotion_data.csv", index=False, encoding="utf-8-sig")
print(f"Data saved, total {len(df)} records")
print("\nData distribution:")
print(df["label"].value_counts())
