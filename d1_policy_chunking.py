
import os
import pandas as pd

# Folder containing policy documents
policy_folder = "data/policies"

# Chunk settings
chunk_size = 40
overlap = 10
step_size = chunk_size - overlap

# Store all chunks
all_chunks = []

# Read each policy document
for filename in os.listdir(policy_folder):

    if filename.endswith(".txt"):

        file_path = os.path.join(policy_folder, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Split document into words
        words = text.split()

        start = 0
        chunk_number = 1

        # Create chunks with overlap
        while start < len(words):

            chunk_words = words[start:start + chunk_size]

            chunk_text = " ".join(chunk_words)

            all_chunks.append({
                "policy_name": filename,
                "chunk_number": chunk_number,
                "chunk_text": chunk_text,
                "word_count": len(chunk_words)
            })

            # Stop when the end of the document is reached
            if start + chunk_size >= len(words):
                break

            start = start + step_size
            chunk_number += 1


# Convert chunks into a DataFrame
chunks_df = pd.DataFrame(all_chunks)

# Create output folder if it does not exist
os.makedirs("outputs", exist_ok=True)

# Save chunks
chunks_df.to_csv("outputs/d1_policy_chunks.csv", index=False)

# Display results
print("D1 - POLICY CHUNKING RESULTS")
print("--------------------------------")

print("\nChunks per policy:")
print(chunks_df.groupby("policy_name").size())

print("\nTotal chunks:", len(chunks_df))

print("\nChunk details:")
print(chunks_df[["policy_name", "chunk_number", "word_count"]].to_string(index=False))

print("\nSaved to outputs/d1_policy_chunks.csv")
