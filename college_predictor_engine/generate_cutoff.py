import pandas as pd

# Load your existing CSV
df = pd.read_csv(r"C:\Users\KIIT\OneDrive\Desktop\Career counselling engine\career_engine\data\colleges_master_final.csv")

def generate_cutoff(row, index):
    exam = str(row["entrance_exam"]).lower()
    tier = str(row["tier"]).lower()

    # JEE ADVANCED
    if "advanced" in exam:
        if "tier1" in tier:
            base = 100
        elif "tier2" in tier:
            base = 800
        else:
            base = 2000
        return base + index * 5

    # JEE MAIN
    elif "main" in exam:
        if "tier1" in tier:
            base = 2000
        elif "tier2" in tier:
            base = 8000
        else:
            base = 20000
        return base + index * 50

    # BITSAT
    elif "bitsat" in exam:
        if "tier1" in tier:
            base = 320
        elif "tier2" in tier:
            base = 280
        else:
            base = 240
        return base + (index % 20)

    # fallback
    return 10000 + index * 100


# Apply cutoff
df["cutoff"] = [generate_cutoff(row, i) for i, row in df.iterrows()]

# Save new file
df.to_csv("colleges_master_final_with_cutoff.csv", index=False)

print("✅ New dataset created with cutoff")