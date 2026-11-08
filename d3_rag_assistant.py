
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import mock_llm

# Load policy chunks created in D1
chunks_df = pd.read_csv("outputs/d1_policy_chunks.csv")

# Convert policy chunks into TF-IDF vectors
chunk_texts = chunks_df["chunk_text"].tolist()

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(chunk_texts)


# Retrieve the three most relevant policy chunks
def retrieve(query, k=3):
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    top_indexes = similarities.argsort()[::-1][:k]

    results = []

    for index in top_indexes:
        results.append({
            "source": chunks_df.iloc[index]["policy_name"],
            "score": similarities[index],
            "text": chunks_df.iloc[index]["chunk_text"]
        })

    return results


# Generate an answer using retrieved policy context
def answer(question):

    results = retrieve(question, k=3)

    context = "CONTEXT:\n"

    for result in results:
        context += "[" + result["source"] + "]\n"
        context += result["text"] + "\n"

    user_message = context + "\nQUESTION:\n" + question

    messages = [
        {
            "role": "system",
            "content": (
                "You are a POLICY ASSISTANT. "
                "Answer the question only using the supplied policy context. "
                "If the information is not available in the context, "
                "say that you could not find the information in the policy documents."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = mock_llm.chat(messages)

    model_answer = response.choices[0].message.content

    sources = []
    for result in results:
        if result["source"] not in sources:
            sources.append(result["source"])

    return model_answer, sources


# Test the RAG assistant
question = "What is the refund policy for late delivery?"

result, sources = answer(question)

print("D3 - RAG POLICY ASSISTANT RESULTS")
print("--------------------------------")
print("Question:", question)
print("\nAnswer:")
print(result)
print("\nSources used:")
for source in sources:
    print("-", source)
