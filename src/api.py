from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv
import torch
from typing import Optional
import tempfile
import pickle  # Ensure this is imported

# ... Path configuration code ...

# =======================================================
# Fix: Ensure Python can find local modules
# Add the directory of the current script (src/) to the Python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# =======================================================


# Import custom modules
# 🚨 暫時註釋 Whisper 以減少部署大小
# from whisper_service import WhisperService
from intent_classification import IntentClassifier
from faq_rag import RAGSystem
from model import TextCNN
from data_processing import Vocabulary, text_to_indices

# ... FastAPI initialization code ...

# ========== Initialize all modules ==========
print("Initializing AI modules...")

# 1. Speech-to-Text Service
# 🚨 暫時註釋 Whisper 以減少部署大小
# whisper_service = WhisperService()
whisper_service = None  # 暫時設為 None

# 2. Emotion Classification Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load the Vocabulary using a custom Unpickler to handle class path issues
print("Loading vocabulary...")


class VocabularyUnpickler(pickle.Unpickler):
    """
    Custom Unpickler to resolve class path issues when deserializing
    the Vocabulary class from a pickle file.
    """

    def find_class(self, module, name):
        if module == "__main__" and name == "Vocabulary":
            return Vocabulary
        return super().find_class(module, name)


try:
    # Try Docker path first, then local path
    vocab_paths = [
        "/app/models/vocab.pkl",  # Docker path
        "../models/vocab.pkl",  # Local path from src/
        "models/vocab.pkl",  # Local path from root
    ]

    vocab_loaded = False
    for vocab_path in vocab_paths:
        if os.path.exists(vocab_path):
            with open(vocab_path, "rb") as f:
                vocab_obj = VocabularyUnpickler(f).load()

            # Ensure the correct format is retrieved
            if hasattr(vocab_obj, "word2idx"):
                vocab = vocab_obj.word2idx
            elif isinstance(vocab_obj, dict):
                vocab = vocab_obj
            else:
                raise TypeError(f"Unexpected vocabulary type: {type(vocab_obj)}")

            print(
                f"✓ Vocabulary loaded successfully from {vocab_path}, size: {len(vocab)}"
            )
            vocab_loaded = True
            break

    if not vocab_loaded:
        raise FileNotFoundError(f"vocab.pkl not found in any of: {vocab_paths}")

except Exception as e:
    print(f"✗ Failed to load vocabulary: {e}")
    import traceback

    traceback.print_exc()
    raise

# Initialize the model
emotion_model = TextCNN(
    vocab_size=len(vocab),
    embed_dim=128,
    num_channels=100,
    kernel_sizes=[3, 4, 5],
    num_classes=3,
    dropout=0.5,
)

# ... The rest of the code remains unchanged ...

# **** Model Parameters End ====

# **** Load pre-trained weights (handle checkpoint format) ====
try:
    # Try Docker path first, then local path
    model_paths = [
        "/app/models/best_model.pth",  # Docker path
        "../models/best_model.pth",  # Local path from src/
        "models/best_model.pth",  # Local path from root
    ]

    model_loaded = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=device)

            # Check if it is a full checkpoint dictionary or just model weights
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                emotion_model.load_state_dict(checkpoint["model_state_dict"])
                epoch = checkpoint.get("epoch", "N/A")
                val_acc = checkpoint.get("val_acc", 0)
                print(
                    f"✓ Emotion model weights loaded successfully from {model_path} "
                    f"(epoch {epoch}, validation accuracy: {val_acc:.2%})"
                )
            else:
                emotion_model.load_state_dict(checkpoint)
                print(f"✓ Emotion model weights loaded successfully from {model_path}")

            model_loaded = True
            break

    if not model_loaded:
        raise FileNotFoundError(f"best_model.pth not found in any of: {model_paths}")

except Exception as e:
    print(f"✗ Failed to load model weights: {e}")
    raise
# **** Load Weights End ====

emotion_model.to(device)
emotion_model.eval()

EMOTION_LABELS = {0: "正面", 1: "中性", 2: "負面"}


def predict_emotion(text: str) -> dict:
    """Predicts the emotion of the input text."""
    indices = text_to_indices(text, vocab, max_len=100)
    input_tensor = torch.LongTensor([indices]).to(device)

    with torch.no_grad():
        output = emotion_model(input_tensor)
        probs = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probs, 1)

    return {
        "emotion": EMOTION_LABELS[predicted.item()],
        "confidence": float(confidence.item()),
    }
    # **** predict_emotion End ====


# 3. Intent Recognition
intent_classifier = IntentClassifier()

# 4. RAG System
rag_system = RAGSystem()

print("All modules initialized successfully!")

# ========== API Endpoint Definitions ==========

# ========== Initialize FastAPI ==========
app = FastAPI(
    title="AI Customer Service Intelligent Analysis System",
    description="Integrates Speech-to-Text, Emotion Analysis, Intent Recognition, and RAG Q&A.",
    version="2.0.0",
)


class TextRequest(BaseModel):
    """Schema for plain text request"""

    text: str
    use_claude: Optional[bool] = False


class PipelineResponse(BaseModel):
    """Schema for full pipeline response"""

    transcription: Optional[str] = None
    emotion: dict
    intent: dict
    rag_response: dict
    final_answer: str


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "version": "2.0.0",
        "modules": {
            "whisper": "ready",
            "emotion": "ready",
            "intent": "ready",
            "rag": "ready",
        },
    }


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint 1: Speech-to-Text
    🚨 暫時停用：為了減少部署大小，Whisper 功能已暫時關閉
    """
    return {
        "error": "語音轉文字功能暫時停用",
        "message": "為了優化部署，此功能已暫時關閉。如需使用，請聯繫管理員。",
    }

    # 原始代碼（已註釋）
    # try:
    #     # Save temporary file
    #     with tempfile.NamedTemporaryFile(
    #         delete=False, suffix=os.path.splitext(file.filename)[1]
    #     ) as tmp:
    #         content = await file.read()
    #         tmp.write(content)
    #         tmp_path = tmp.name
    #
    #     # Transcribe
    #     result = whisper_service.transcribe(tmp_path)
    #
    #     # Delete temporary file
    #     os.unlink(tmp_path)
    #
    #     if "error" in result:
    #         raise HTTPException(status_code=500, detail=result["error"])
    #
    #     return result
    #
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
def analyze_text(request: TextRequest):
    """
    Endpoint 2: Analyze Text (Emotion + Intent)
    """
    try:
        emotion = predict_emotion(request.text)
        intent = intent_classifier.predict_with_rules(request.text)

        return {"text": request.text, "emotion": emotion, "intent": intent}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: TextRequest):
    """
    Endpoint 3: Intelligent Q&A (RAG)
    """
    try:
        # Step 1: Analyze emotion and intent
        emotion = predict_emotion(request.text)
        intent = intent_classifier.predict_with_rules(request.text)

        # Step 2: RAG response generation
        rag_response = rag_system.generate_response(
            query=request.text,
            emotion=emotion["emotion"],
            intent=intent["intent"],
            use_claude=request.use_claude,
        )

        return {
            "query": request.text,
            "emotion": emotion,
            "intent": intent,
            "answer": rag_response["answer"],
            "retrieved_faqs": rag_response["retrieved_faqs"],
            "model": rag_response["model"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline", response_model=PipelineResponse)
async def full_pipeline(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    use_claude: bool = Form(False),
):
    """
    Endpoint 4: Full Pipeline (Audio -> Text -> Analysis -> Q&A)

    Supports two types of input:
    1. Uploaded audio file (file)
    2. Direct text input (text)
    """
    try:
        # Step 1: Get text input
        if file:
            # 🚨 語音轉文字功能暫時停用
            raise HTTPException(
                status_code=503,
                detail="語音轉文字功能暫時停用。為了優化部署，此功能已暫時關閉。請直接使用文字輸入。",
            )

        # 原始代碼（已註釋）
        # # Transcribe from audio file
        # with tempfile.NamedTemporaryFile(
        #     delete=False, suffix=os.path.splitext(file.filename)[1]
        # ) as tmp:
        #     content = await file.read()
        #     tmp.write(content)
        #     tmp_path = tmp.name
        #
        # transcription_result = whisper_service.transcribe(tmp_path)
        # os.unlink(tmp_path)
        #
        # if "error" in transcription_result:
        #     raise HTTPException(
        #         status_code=500, detail=transcription_result["error"]
        #     )
        #
        # input_text = transcription_result["text"]

        if text:
            input_text = text
            transcription = None
        else:
            raise HTTPException(
                status_code=400, detail="Must provide either 'file' or 'text'"
            )

        # Step 2: Emotion Analysis
        emotion = predict_emotion(input_text)

        # Step 3: Intent Recognition
        intent = intent_classifier.predict_with_rules(input_text)

        # Step 4: RAG response generation
        rag_response = rag_system.generate_response(
            query=input_text,
            emotion=emotion["emotion"],
            intent=intent["intent"],
            use_claude=use_claude,
        )

        return PipelineResponse(
            transcription=transcription,
            emotion=emotion,
            intent=intent,
            rag_response=rag_response,
            final_answer=rag_response["answer"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Startup Command ==========

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,  # Pass the app object directly
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=False,  # Disable hot reload for production/container
    )
