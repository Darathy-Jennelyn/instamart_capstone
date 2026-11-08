
import os

checks = {
    "refund_policy.txt": "more than 45 minutes",
    "payment_policy.txt": "48 hours"
}

for filename, phrase in checks.items():

    path = os.path.join("data/policies", filename)

    with open(path, "r", encoding="utf-8") as file:
        words = file.read().split()

    phrase_words = phrase.split()

    print("\nPolicy:", filename)
    print("Expected fact:", phrase)

    for i in range(len(words) - len(phrase_words) + 1):

        if words[i:i + len(phrase_words)] == phrase_words:

            start_chunk = i // 40
            end_chunk = (i + len(phrase_words) - 1) // 40

            print("Word positions:", i, "to", i + len(phrase_words) - 1)
            print("Chunk containing start:", start_chunk + 1)
            print("Chunk containing end:", end_chunk + 1)

            if start_chunk != end_chunk:
                print("The expected fact crosses a chunk boundary.")

            for boundary in range(40, len(words), 40):
                if abs(boundary - i) <= 40:
                    print("\nBoundary at word:", boundary)
                    print("Previous chunk ends:", words[max(0, boundary-8):boundary])
                    print("Next chunk starts:", words[boundary:boundary+8])
