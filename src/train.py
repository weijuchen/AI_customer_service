import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
from data_processing import prepare_data
from model import TextCNN, EmotionLSTM
from typing import Tuple, Dict, Any


def train_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    """Trains the model for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    progress_bar = tqdm(dataloader, desc="Training")
    for batch in progress_bar:
        texts = batch["text"].to(device)
        labels = batch["label"].to(device)

        # Forward pass
        optimizer.zero_grad()
        outputs = model(texts)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        # Calculate accuracy
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        total_loss += loss.item()

        # Update progress bar
        progress_bar.set_postfix(
            {"loss": f"{loss.item():.4f}", "acc": f"{100 * correct / total:.2f}%"}
        )

    avg_loss = total_loss / len(dataloader)
    accuracy = 100 * correct / total
    return avg_loss, accuracy


def evaluate(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    """Evaluates the model."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            texts = batch["text"].to(device)
            labels = batch["label"].to(device)

            outputs = model(texts)
            loss = criterion(outputs, labels)

            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    accuracy = 100 * correct / total
    return avg_loss, accuracy


def plot_history(
    train_losses: List[float],
    val_losses: List[float],
    train_accs: List[float],
    val_accs: List[float],
) -> None:
    """Plots the training curves and saves the figure."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Loss curve
    ax1.plot(train_losses, label="Train Loss")
    ax1.plot(val_losses, label="Val Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training and Validation Loss")
    ax1.legend()
    ax1.grid(True)

    # Accuracy curve
    ax2.plot(train_accs, label="Train Acc")
    ax2.plot(val_accs, label="Val Acc")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.set_title("Training and Validation Accuracy")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    # Ensure the models directory exists before saving
    os.makedirs("../models", exist_ok=True)
    plt.savefig("../models/training_history.png")
    print("Training curves saved to models/training_history.png")


def main():
    # Set parameters
    BATCH_SIZE = 16
    EPOCHS = 20
    LEARNING_RATE = 0.001
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Using device: {DEVICE}")

    # Prepare data
    print("\nPreparing data...")
    train_loader, val_loader, vocab = prepare_data(
        "../data/emotion_data_augmented.csv", batch_size=BATCH_SIZE
    )

    # Initialize model
    print("\nInitializing model...")
    model = TextCNN(
        vocab_size=len(vocab.word2idx),
        embed_dim=128,
        num_classes=3,
        kernel_sizes=[3, 4, 5],
        num_channels=100,
        dropout=0.5,
    )
    model = model.to(DEVICE)

    # Calculate number of model parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total model parameters: {total_params:,}")

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    print("\nStarting training...")
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []
    best_val_acc = 0

    # Ensure models directory exists for saving checkpoints
    os.makedirs("../models", exist_ok=True)

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")

        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, DEVICE
        )

        # Validate
        val_loss, val_acc = evaluate(model, val_loader, criterion, DEVICE)

        # Record metrics
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)

        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        # Save the best model based on validation accuracy
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_acc": val_acc,
                },
                "../models/best_model.pth",
            )
            print(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")

    # Plot and save training curves
    plot_history(train_losses, val_losses, train_accs, val_accs)

    print(f"\nTraining finished! Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: models/best_model.pth")


if __name__ == "__main__":
    main()
