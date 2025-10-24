import torch
import torch.nn as nn
import torch.nn.functional as F


class TextCNN(nn.Module):
    """Text Classification CNN Model"""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        num_classes: int = 3,
        kernel_sizes: List[int] = [3, 4, 5],
        num_channels: int = 100,
        dropout: float = 0.5,
    ):
        super(TextCNN, self).__init__()

        # Embedding layer (padding_idx=0 for <PAD> token)
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # Multiple Convolutional layers (with different kernel sizes)
        self.convs = nn.ModuleList(
            [
                nn.Conv1d(
                    in_channels=embed_dim, out_channels=num_channels, kernel_size=k
                )
                for k in kernel_sizes
            ]
        )

        # Dropout layer
        self.dropout = nn.Dropout(dropout)

        # Fully connected layer
        self.fc = nn.Linear(len(kernel_sizes) * num_channels, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch_size, seq_len]

        # Embedding: [batch_size, seq_len, embed_dim]
        embedded = self.embedding(x)

        # Transpose to fit Conv1d format: [batch_size, embed_dim, seq_len]
        embedded = embedded.permute(0, 2, 1)

        # Apply multiple convolutions and max-pooling
        conv_outputs = []
        for conv in self.convs:
            # Convolution: [batch_size, num_channels, seq_len - kernel_size + 1]
            conv_out = F.relu(conv(embedded))
            # Max pooling over time dimension: [batch_size, num_channels, 1]
            pooled = F.max_pool1d(conv_out, conv_out.shape[2])
            # Squeeze: [batch_size, num_channels]
            pooled = pooled.squeeze(2)
            conv_outputs.append(pooled)

        # Concatenate all convolutional outputs: [batch_size, len(kernel_sizes) * num_channels]
        concat = torch.cat(conv_outputs, dim=1)

        # Dropout
        dropped = self.dropout(concat)

        # Fully connected layer: [batch_size, num_classes]
        output = self.fc(dropped)

        return output


class EmotionLSTM(nn.Module):
    """Alternative Model: LSTM for Text Classification"""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        hidden_dim: int = 256,
        num_classes: int = 3,
        num_layers: int = 2,
        dropout: float = 0.5,
    ):
        super(EmotionLSTM, self).__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout,
        )
        self.fc = nn.Linear(
            hidden_dim * 2, num_classes
        )  # *2 because it's bidirectional
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch_size, seq_len]
        embedded = self.embedding(x)  # [batch_size, seq_len, embed_dim]
        # lstm_out: [batch_size, seq_len, hidden_dim * 2]
        # hidden, cell: [num_layers*2, batch_size, hidden_dim]
        lstm_out, (hidden, cell) = self.lstm(embedded)

        # Use the hidden state from the last time step
        # Extract the hidden state of the last layer (forward and backward)
        hidden_fwd = hidden[-2, :, :]  # [batch_size, hidden_dim]
        hidden_bwd = hidden[-1, :, :]  # [batch_size, hidden_dim]

        # Concatenate: [batch_size, hidden_dim*2]
        concat = torch.cat([hidden_fwd, hidden_bwd], dim=1)
        dropped = self.dropout(concat)
        output = self.fc(dropped)

        return output


if __name__ == "__main__":
    # Test models
    vocab_size = 1000
    batch_size = 4
    seq_len = 50

    # Test TextCNN
    model_cnn = TextCNN(vocab_size=vocab_size)
    x = torch.randint(0, vocab_size, (batch_size, seq_len))
    output = model_cnn(x)
    print("TextCNN output shape:", output.shape)  # Should be [4, 3]

    # Test LSTM
    model_lstm = EmotionLSTM(vocab_size=vocab_size)
    output = model_lstm(x)
    print("LSTM output shape:", output.shape)  # Should be [4, 3]
