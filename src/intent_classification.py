from transformers import BertTokenizer, BertForSequenceClassification
import torch
from typing import Dict, List, Any


class IntentClassifier:
    """BERT-based Intent Recognition Classifier"""

    # Define intent labels
    INTENT_LABELS: Dict[int, str] = {
        0: "查詢訂單",  # Order Inquiry
        1: "退換貨問題",  # Return/Exchange Issue
        2: "物流配送",  # Logistics/Delivery
        3: "產品諮詢",  # Product Inquiry
        4: "帳號問題",  # Account Issue
        5: "投訴建議",  # Complaint/Suggestion
        6: "其他",  # Other
    }

    def __init__(self, use_pretrained: bool = True):
        """
        Initializes the BERT model.

        Args:
            use_pretrained: Whether to use the pre-trained model
                            (Can be fine-tuned later if needed).
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Intent Classifier using device: {self.device}")

        # Use Chinese BERT model
        model_name = "bert-base-chinese"
        try:
            self.tokenizer = BertTokenizer.from_pretrained(model_name)

            if use_pretrained:
                # Use pre-trained BERT + simple classification head
                self.model = BertForSequenceClassification.from_pretrained(
                    model_name, num_labels=len(self.INTENT_LABELS)
                )

            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Failed to load BERT model components: {e}")
            # Initialize with dummy attributes if loading fails (e.g., no internet/files)
            self.tokenizer = None
            self.model = None

    def predict(self, text: str) -> dict:
        """
        Predicts the intent of the input text using the BERT model.

        Args:
            text: Input text string.

        Returns:
            {"intent": "intent name", "confidence": 0.95, "intent_id": 0}
        """
        if not self.model or not self.tokenizer:
            return {
                "intent": "其他",
                "confidence": 0.0,
                "intent_id": 6,
                "error": "Model not loaded",
            }

        # Tokenize
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=128, padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            confidence, predicted = torch.max(probs, dim=-1)

        intent_id = predicted.item()
        intent_name = self.INTENT_LABELS.get(intent_id, "其他")

        return {
            "intent": intent_name,
            "confidence": float(confidence.item()),
            "intent_id": intent_id,
        }

    def predict_with_rules(self, text: str) -> dict:
        """
        Combines rule-based matching and BERT prediction for enhanced accuracy.
        """
        # Keyword-based rules
        rules: Dict[str, List[str]] = {
            "退換貨問題": ["退貨", "退款", "換貨", "不滿意", "瑕疵"],
            "查詢訂單": ["訂單", "查詢", "進度", "何時到", "出貨"],
            "物流配送": ["運費", "配送", "物流", "宅配", "郵寄"],
            "產品諮詢": ["規格", "功能", "尺寸", "顏色", "材質", "怎麼用"],
            "帳號問題": ["密碼", "登入", "註冊", "會員", "帳號"],
            "投訴建議": ["投訴", "客訴", "建議", "不滿", "態度"],
        }

        # Look up intent ID for rule-based matching
        intent_name_list = list(self.INTENT_LABELS.values())

        # 1. Match using rules first
        for intent, keywords in rules.items():
            if any(keyword in text for keyword in keywords):
                return {
                    "intent": intent,
                    "confidence": 0.95,  # Assign high confidence for rule-based match
                    "intent_id": intent_name_list.index(intent),
                    "method": "rule-based",
                }

        # 2. If no rule matches, use the BERT model
        result = self.predict(text)
        result["method"] = "bert"
        return result


# Test Code
if __name__ == "__main__":
    classifier = IntentClassifier()

    test_texts = [
        "我想退貨，商品有瑕疵",
        "請問我的訂單什麼時候會到",
        "運費怎麼計算",
        "這個產品有哪些顏色",
        "你們的服務真的很差",  # Should hit rule
        "我無法登入我的會員帳號",  # Should hit rule
        "純粹閒聊",  # Should hit BERT, likely to be '其他'
    ]

    print("\n=== Intent Classification Test ===")
    for text in test_texts:
        result = classifier.predict_with_rules(text)
        print(f"\nText: {text}")
        print(
            f"Intent: {result.get('intent')} (Confidence: {result.get('confidence', 0.0):.2f})"
        )
        print(f"Method: {result.get('method')}")
