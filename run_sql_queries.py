
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("data/instamart.db")

# Read SQL queries
with open("sql/queries.sql", "r") as file:
    queries = file.read().split(";")

# Run each query
for i, query in enumerate(queries, start=1):
    if query.strip():
        result = pd.read_sql_query(query, conn)

        print(f"\nQ{i} Results")
        print("Rows:", len(result))
        print(result.head(5))

        if i == 2:
            print("Total revenue:", round(result["revenue"].sum(), 2))

        elif i == 5:
            print(
                "Average customer spend:",
                round(result["total_spend"].mean(), 2)
            )

        elif i == 6:
            print(
                "Rows where RANK differs from ROW_NUMBER:",
                len(result[result["rank"] != result["row_number"]])
            )
            print(result[result["rank"] == 1][
                    ["city", "customer_id", "total_spend"]])

        elif i == 7:
            print(
                "Final cumulative revenue:",
                result["cumulative_revenue"].iloc[-1]
            )

conn.close()
