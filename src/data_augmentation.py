import pandas as pd


def augment_text(text):
    """Simple data augmentation method"""
    # Method 1: Random punctuation insertion
    augmented = []

    # Original text
    augmented.append(text)

    # Add exclamation mark
    if "!" not in text and "！" not in text:
        augmented.append(text + "！")

    # Add question mark
    if "?" not in text and "？" not in text:
        augmented.append(text + "？")

    return augmented


# Read data
df = pd.read_csv("../data/emotion_data.csv")
# df.to_csv("../data/emotion_data.csv", index=False, encoding="utf-8-sig") # Example of saving original data (commented out)

# Augment data
augmented_data = []
for idx, row in df.iterrows():
    texts = augment_text(row["text"])
    for text in texts:
        augmented_data.append({"text": text, "label": row["label"]})

# Save augmented data
df_aug = pd.DataFrame(augmented_data)
df_aug.to_csv("../data/emotion_data_augmented.csv", index=False, encoding="utf-8-sig")

print(f"Original data size: {len(df)} records")
print(f"Augmented data size: {len(df_aug)} records")
