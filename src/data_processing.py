

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import jieba
from collections import Counter
import pickle
from typing import Dict, List, Any


class Vocabulary:
    """Vocabulary class for text to index mapping"""

    def __init__(self):
        self.word2idx: Dict[str, int] = {"<PAD>": 0, "<UNK>": 1}
        self.idx2word: Dict[int, str] = {0: "<PAD>", 1: "<UNK>"}
        self.word_count: Counter = Counter()

    def add_sentence(self, sentence: str) -> None:
        """Adds a sentence to the vocabulary for word counting."""
        # Use jieba for Chinese word segmentation
        words = jieba.lcut(sentence)
        for word in words:
            self.word_count[word] += 1

    def build_vocab(self, min_freq: int = 1) -> None:
        """Builds the final vocabulary based on word counts."""
        idx = 2  # Start index from 2, as 0 and 1 are reserved for <PAD> and <UNK>
        for word, count in self.word_count.items():
            if count >= min_freq:
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                idx += 1
        print(f"Vocabulary size: {len(self.word2idx)}")

    def encode(self, sentence: str, max_len: int = 50) -> List[int]:
        """Encodes a sentence into a sequence of indices, applying padding/truncation."""
        words = jieba.lcut(sentence)
        indices = []
        # Convert words to indices
        for word in words:
            if word in self.word2idx:
                indices.append(self.word2idx[word])
            else:
                indices.append(self.word2idx["<UNK>"])

        # Padding or truncation
        if len(indices) < max_len:
            indices += [self.word2idx["<PAD>"]] * (max_len - len(indices))
        else:
            indices = indices[:max_len]

        return indices

    def save(self, filepath: str) -> None:
        """Saves the Vocabulary object using pickle."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath: str) -> "Vocabulary":
        """Loads the Vocabulary object from a file."""
        with open(filepath, "rb") as f:
            return pickle.load(f)


class EmotionDataset(Dataset):
    """Custom Dataset for emotion classification"""

    def __init__(
        self, texts: List[str], labels: List[int], vocab: Vocabulary, max_len: int = 50
    ):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]

        # Encode text
        encoded = self.vocab.encode(text, self.max_len)

        return {
            "text": torch.tensor(encoded, dtype=torch.long),
            "label": torch.tensor(label, dtype=torch.long),
        }


def prepare_data(csv_path: str, test_size: float = 0.2, batch_size: int = 16) -> Any:
    """Prepares training and validation data loaders."""
    # Read data
    df = pd.read_csv(csv_path)

    # Build vocabulary
    vocab = Vocabulary()
    for text in df["text"]:
        vocab.add_sentence(text)
    vocab.build_vocab(min_freq=1)

    # Save vocabulary
    vocab.save("../models/vocab.pkl")

    # Split training and validation sets
    from sklearn.model_selection import train_test_split

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=test_size,
        random_state=42,
        stratify=df["label"],  # Maintain class proportion
    )

    # Create Dataset instances
    train_dataset = EmotionDataset(train_texts, train_labels, vocab)
    val_dataset = EmotionDataset(val_texts, val_labels, vocab)

    # Create DataLoader instances
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    print(f"Training set size: {len(train_dataset)}")
    print(f"Validation set size: {len(val_dataset)}")

    return train_loader, val_loader, vocab


# ========== Compatibility Functions (for use in api.py) ==========


def load_vocab(vocab_path: str) -> Dict[str, int]:
    """
    Loads the vocabulary and returns the word-to-index dictionary.

    Args:
        vocab_path: Path to the vocabulary pickle file.

    Returns:
        The word-to-index dictionary {word: idx}.
    """
    with open(vocab_path, "rb") as f:
        vocab_obj = pickle.load(f)

    # If it's a Vocabulary object, return its word2idx attribute
    if isinstance(vocab_obj, Vocabulary):
        return vocab_obj.word2idx
    # If it's already a dictionary, return it directly
    elif isinstance(vocab_obj, dict):
        return vocab_obj
    else:
        raise TypeError(f"Unknown vocabulary type: {type(vocab_obj)}")


def text_to_indices(text: str, vocab: Dict[str, int], max_len: int = 100) -> List[int]:
    """
    Converts text to a sequence of indices (compatibility function).

    Args:
        text: Input text.
        vocab: The vocabulary in dictionary format {word: idx}.
        max_len: Maximum sequence length.

    Returns:
        A list of indices.
    """
    # Tokenization
    words = jieba.lcut(text)

    # Convert to indices, using UNK index 1 if word is not found
    indices = [vocab.get(word, vocab.get("<UNK>", 1)) for word in words]
    pad_idx = vocab.get("<PAD>", 0)

    # Padding or truncation
    if len(indices) < max_len:
        indices += [pad_idx] * (max_len - len(indices))
    else:
        indices = indices[:max_len]

    return indices


# ========== Test Code ==========
if __name__ == "__main__":
    import sys
    import io
    import os
    import shutil  # Import shutil for cleanup

    # Fix encoding for Windows
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Define model path
    model_dir = "../models"
    vocab_path = os.path.join(model_dir, "vocab.pkl")
    test_vocab_path = os.path.join("models", "vocab.pkl")

    print("=" * 50)
    print("data_processing.py Test")
    print("=" * 50)

    # Create dummy models directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)

    # Test compatibility functions
    print("\nTesting Compatibility Functions:")

    # Check if vocab.pkl exists
    if os.path.exists(vocab_path):
        print(f"✓ Found vocabulary file: {vocab_path}")

        # Test load_vocab
        vocab_dict = load_vocab(vocab_path)
        print(f"✓ Vocabulary loaded successfully, size: {len(vocab_dict)}")
        print(f"  First 5 words: {list(vocab_dict.items())[:5]}")

        # Test text_to_indices
        test_text = "我要退貨"
        indices = text_to_indices(test_text, vocab_dict, max_len=20)
        print(f"\n✓ Text to Indices Test:")
        print(f"  Text: {test_text}")
        print(f"  Indices: {indices[:10]}...")
    else:
        print(f"✗ Vocabulary file not found: {vocab_path}")
        print("  Creating a test vocabulary for demonstration...")

        # Create a test vocabulary
        vocab = Vocabulary()
        test_sentences = ["我要退貨", "商品很好", "客服態度不錯"]
        for sent in test_sentences:
            vocab.add_sentence(sent)
        vocab.build_vocab()

        # Save test vocab (using a temporary path for testing)
        os.makedirs("models", exist_ok=True)
        vocab.save(test_vocab_path)
        print(f"✓ Test vocabulary saved to: {test_vocab_path}")

        # Test loading the created test vocab
        vocab_dict = load_vocab(test_vocab_path)
        indices = text_to_indices("我要退貨", vocab_dict, max_len=20)
        print(f"  Test loading and encoding successful. Indices: {indices[:10]}...")

        # Clean up test vocab
        if os.path.exists(test_vocab_path):
            os.remove(test_vocab_path)
        if os.path.exists("models") and not os.listdir("models"):
            os.rmdir("models")
        print("  Test vocabulary cleaned up.")

    print("\n" + "=" * 50)
    print("✓ Test finished")
    print("=" * 50)
