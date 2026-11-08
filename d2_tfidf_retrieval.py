
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load policy chunks created in D1
chunks_df = pd.read_csv("outputs/d1_policy_chunks.csv")

# Get the text of all policy chunks
chunk_texts = chunks_df["chunk_text"].tolist()

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Convert policy chunks into TF-IDF vectors
tfidf_matrix = vectorizer.fit_transform(chunk_texts)


# Function to retrieve relevant policy chunks
def retrieve(query, k=3):

    # Convert the search query into a TF-IDF vector
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    # Get the indexes of top matching chunks
    top_indexes = similarities.argsort()[::-1][:k]

    # Store retrieved results
    results = []

    for index in top_indexes:

        results.append({
            "source": chunks_df.iloc[index]["policy_name"],
            "score": similarities[index],
            "text": chunks_df.iloc[index]["chunk_text"]
        })

    return results


# Test the retrieval function
query = "refund policy late delivery"

results = retrieve(query, k=3)

print("D2 - TF-IDF RETRIEVAL RESULTS")
print("--------------------------------")

print("\nSearch query:", query)

for i, result in enumerate(results):

    print("\nResult", i + 1)
    print("Source:", result["source"])
    print("Similarity score:", round(result["score"], 4))
    print("Text:", result["text"])
