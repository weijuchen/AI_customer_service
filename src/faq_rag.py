import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI

# from anthropic import Anthropic

from dotenv import load_dotenv, find_dotenv
import os

# Find the actual path of .env
dotenv_path = find_dotenv()
print(f"Loaded .env path: {dotenv_path}")

# Load .env variables
load_dotenv(dotenv_path, override=True)

# load_dotenv()


class RAGSystem:
    """Simplified RAG System: FAQ Retrieval + LLM Generation"""

    def __init__(self, faq_path: str = "/app/faq_data/faq.json"):
        """
        Initializes the RAG System

        Args:
            faq_path: Path to the FAQ knowledge base (absolute path for container environment).
        """
        # Load FAQs
        try:
            with open(faq_path, "r", encoding="utf-8") as f:
                self.faqs = json.load(f)
        except FileNotFoundError:
            print(f"Error: FAQ file not found at {faq_path}")
            self.faqs = []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {faq_path}")
            self.faqs = []

        # Initialize Sentence Transformer (for semantic retrieval)
        print("Loading Sentence Transformer model...")
        self.encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # Build FAQ vector index
        if self.faqs:
            self._build_index()
        else:
            self.index = None
            print("No FAQs loaded. Index building skipped.")

        # Initialize LLM client (OpenAI is used here)
        # Note: Using an explicit key for demonstration, but environment variables are recommended
        # self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Explicit key for testing/demo purposes (replace with a proper key or env var in production)

        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # self.anthropic_client = (
        #     Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        #     if os.getenv("ANTHROPIC_API_KEY") else None
        # )

    def _build_index(self) -> None:
        """Builds the FAISS vector index."""
        print("Building FAISS vector index for FAQs...")

        # Encode all FAQ questions into vectors
        questions = [faq["question"] for faq in self.faqs]
        self.question_embeddings = self.encoder.encode(questions, convert_to_numpy=True)

        # Create FAISS index
        dimension = self.question_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance index
        self.index.add(self.question_embeddings)

        print(f"Index building completed with {len(self.faqs)} FAQs.")

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """
        Retrieves the most relevant FAQs.

        Args:
            query: The user's query text.
            top_k: Number of top results to return.

        Returns:
            A list of relevant FAQ dictionaries, including a similarity score:
            [{"question": "...", "answer": "...", "similarity_score": 0.85}, ...]
        """
        if not self.index:
            return []

        # Encode the query into a vector
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)

        # Search in FAISS
        distances, indices = self.index.search(query_embedding, top_k)

        # Assemble results (lower distance is better similarity, convert to score)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Simple conversion to a 0-1 score (higher is better similarity)
            score = 1 / (1 + dist)
            results.append({**self.faqs[idx], "similarity_score": float(score)})

        return results

    def generate_response(
        self, query: str, emotion: str, intent: str, use_claude: bool = False
    ) -> dict:
        """
        Generates a response using RAG.

        Args:
            query: User's question.
            emotion: Emotion label.
            intent: Intent label.
            use_claude: Whether to use Claude (otherwise uses GPT).

        Returns:
            {"answer": "response content", "retrieved_faqs": [...], "model": "gpt-4o-mini"}
        """
        # 1. Retrieve relevant FAQs
        retrieved_faqs = self.retrieve(query, top_k=2)

        # 2. Construct Prompt
        context = "\n\n".join(
            [
                f"FAQ: {faq['question']}\nAnswer: {faq['answer']}"
                for faq in retrieved_faqs
            ]
        )

        prompt = f"""You are a professional customer service assistant. Please answer the user's question based on the following information:

User Emotion: {emotion}
User Intent: {intent}
User Question: {query}

Reference FAQ Knowledge Base:
{context}

Please respond in a friendly and professional tone. If the FAQ does not contain a completely suitable answer, please use the known information to deduce a response, and suggest the user contact a human agent.

Answer:"""

        # 3. Call LLM for generation
        try:
            # Currently only using OpenAI, ignore use_claude flag for simplicity in this file
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            model_used = "gpt-4o-mini"

            return {
                "answer": answer.strip(),
                "retrieved_faqs": retrieved_faqs,
                "model": model_used,
            }

        except Exception as e:
            return {
                "answer": f"Sorry, an error occurred while generating the response: {str(e)}",
                "retrieved_faqs": retrieved_faqs,
                "model": "error",
            }


# Test code
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Note: For this test to run successfully outside the Docker environment,
    # ensure 'faq_data/faq.json' exists relative to the execution path.
    # We use a relative path here for local testing.

    # Try using the path relative to the script for local testing if the absolute path fails
    script_dir = os.path.dirname(__file__)
    local_faq_path = os.path.join(script_dir, "../faq_data/faq.json")

    # Check if the FAQ file exists locally, otherwise use the default path
    if os.path.exists(local_faq_path):
        rag = RAGSystem(faq_path=local_faq_path)
    else:
        print(
            f"Warning: Local FAQ path not found at {local_faq_path}. Using default path /app/faq_data/faq.json."
        )
        rag = RAGSystem()

    # Test Retrieval
    print("\n=== Testing FAQ Retrieval ===")
    query = "我要退貨"
    results = rag.retrieve(query, top_k=2)
    print(f"Query: {query}")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Question: {result['question']}")
        print(f"  Similarity: {result['similarity_score']:.3f}")

    # Test Generation
    print("\n=== Testing RAG Generation ===")
    response = rag.generate_response(
        query="我想退貨但不知道怎麼辦", emotion="負面", intent="退換貨問題"
    )
    print(f"Answer: {response['answer']}")
    print(f"Model Used: {response['model']}")
