
import os
import pandas as pd
import mock_llm

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load evaluation questions
eval_df = pd.read_csv("data/raw/policy_eval.csv")


# Function to create a retrieval system
def create_retriever(chunks_df):

    chunk_texts = chunks_df["chunk_text"].tolist()

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunk_texts)

    def retrieve(query, k=3):

        query_vector = vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector, tfidf_matrix
        )[0]

        top_indexes = similarities.argsort()[::-1][:k]

        results = []

        for index in top_indexes:
            results.append({
                "source": chunks_df.iloc[index]["policy_name"],
                "score": similarities[index],
                "text": chunks_df.iloc[index]["chunk_text"]
            })

        return results

    return retrieve


# Function to generate an answer using retrieved chunks
def answer(question, retrieve):

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
                "Answer only using the supplied context. "
                "If the information is not available, "
                "say you could not find the information in the policy documents."
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


# Function to evaluate all questions
def evaluate(retrieve, evaluation_name):

    results = []

    for _, row in eval_df.iterrows():

        question = row["question"]
        expected_doc = row["expected_doc"]
        expected_fact = row["expected_fact"]

        model_answer, sources = answer(question, retrieve)

        if expected_doc == "NONE":

            fallback_correct = model_answer.startswith(
                "I could not find"
            )

            results.append({
                "question": question,
                "answer": model_answer,
                "sources": ", ".join(sources),
                "fallback_correct": fallback_correct
            })

        else:

            document_found = expected_doc in sources

            fact_found = (
                pd.notna(expected_fact)
                and expected_fact in model_answer
            )

            results.append({
                "question": question,
                "answer": model_answer,
                "sources": ", ".join(sources),
                "document_found": document_found,
                "fact_found": fact_found
            })

    results_df = pd.DataFrame(results)

    # Calculate evaluation scores
    answerable = results_df[
        results_df["question"].isin(
            eval_df[eval_df["expected_doc"] != "NONE"]["question"]
        )
    ]

    unanswerable = results_df[
        results_df["question"].isin(
            eval_df[eval_df["expected_doc"] == "NONE"]["question"]
        )
    ]

    document_score = answerable["document_found"].sum()
    fact_score = answerable["fact_found"].sum()
    fallback_score = unanswerable["fallback_correct"].sum()

    print("\n", evaluation_name)
    print("--------------------------------")

    print("Answerable questions:", len(answerable))
    print(
        "Expected document found:",
        document_score, "/", len(answerable)
    )
    print(
        "Expected fact found in answer:",
        fact_score, "/", len(answerable)
    )
    print("Unanswerable questions:", len(unanswerable))
    print(
        "Correct fallback responses:",
        fallback_score, "/", len(unanswerable)
    )

    return results_df


# ------------------------------------------
# PART 1: NORMAL EVALUATION WITH 10-WORD OVERLAP
# ------------------------------------------

normal_chunks = pd.read_csv("outputs/d1_policy_chunks.csv")

normal_retrieve = create_retriever(normal_chunks)

normal_results = evaluate(
    normal_retrieve,
    "D4 - NORMAL CHUNK EVALUATION"
)


# ------------------------------------------
# PART 2: ZERO-OVERLAP CHUNKING
# ------------------------------------------

policy_folder = "data/policies"

chunk_size = 40
zero_chunks = []

for filename in os.listdir(policy_folder):

    if filename.endswith(".txt"):

        file_path = os.path.join(policy_folder, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        words = text.split()

        start = 0
        chunk_number = 1

        while start < len(words):

            chunk_words = words[start:start + chunk_size]

            zero_chunks.append({
                "policy_name": filename,
                "chunk_number": chunk_number,
                "chunk_text": " ".join(chunk_words),
                "word_count": len(chunk_words)
            })

            start = start + chunk_size
            chunk_number += 1


zero_chunks_df = pd.DataFrame(zero_chunks)

os.makedirs("outputs", exist_ok=True)

zero_chunks_df.to_csv(
    "outputs/d4_zero_overlap_chunks.csv",
    index=False
)

print("\nZero-overlap chunk counts:")
print(zero_chunks_df.groupby("policy_name").size())
print("Total chunks:", len(zero_chunks_df))


# Evaluate using zero-overlap chunks
zero_retrieve = create_retriever(zero_chunks_df)

zero_results = evaluate(
    zero_retrieve,
    "D4 - ZERO-OVERLAP EVALUATION"
)


# Save both evaluation results
normal_results.to_csv(
    "outputs/d4_normal_evaluation.csv",
    index=False
)

zero_results.to_csv(
    "outputs/d4_zero_overlap_evaluation.csv",
    index=False
)


# Show answerable questions that failed in zero-overlap evaluation
print("\nZERO-OVERLAP FAILURES")
print("--------------------------------")

for _, row in zero_results.iterrows():

    original = eval_df[
        eval_df["question"] == row["question"]
    ].iloc[0]

    if original["expected_doc"] != "NONE":

        if not row["document_found"] or not row["fact_found"]:

            print("\nQuestion:", row["question"])
            print("Expected document:", original["expected_doc"])
            print("Expected fact:", original["expected_fact"])
            print("Retrieved sources:", row["sources"])
            print("Generated answer:", row["answer"])
