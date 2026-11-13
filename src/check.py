
import pandas as pd

reviews = pd.read_csv("../data/processed/reviews.csv")

# Group records by review_id
"""groups = reviews.groupby("review_id")

# Count the number of distinct values per column
duplicate_ids = reviews[
    reviews["review_id"].duplicated(keep=False)
]["review_id"].unique()

for review_id in duplicate_ids[:5]:
    group = groups.get_group(review_id)

    print("\nReview ID:", review_id)
    print("Number of records:", len(group))

    for column in reviews.columns:
        print(
            column,
            "->",
            group[column].nunique(dropna=False),
            "distinct values"
        )"""
duplicate_counts = (
    reviews.groupby("review_id")
    .size()
    .value_counts()
    .sort_index()
)

print(duplicate_counts)