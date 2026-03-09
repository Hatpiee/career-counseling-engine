import pandas as pd

df = pd.read_excel("data/colleges_fixed.xlsx")

print("\nColumns:\n", df.columns)

print("\nFirst 10 rows:\n")
print(df.head(10))

print("\nNumber of rows:", len(df))

print("\nMissing college names:")
print(df["college_name_y"].isna().sum())