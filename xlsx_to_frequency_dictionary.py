# --- Imports ---
import pandas as pd
from collections import Counter

def export_keywords(file_path, output_file="./symspell_frequency_dictionary.txt"):
    """
    Extracts keywords from an Excel file and writes them to a SymSpell dictionary.

    Args:
        file_path (str): Path to the Excel spreadsheet.
        output_file (str): Path to output dictionary file.
    """
    # Load Excel
    df = pd.read_excel(file_path)

    # Find 'keywords' column (case-insensitive)
    keyword_col = next(
        (col for col in df.columns if col.strip().lower() == "keywords"), 
        None
    )
    if not keyword_col:
        raise ValueError(
            f"'keywords' column not found. Available columns: {df.columns.tolist()}"
        )

    # --- Step 1: Extract & normalize keywords ---
    keywords = []
    for cell in df[keyword_col].dropna():
        terms = str(cell).split(",")
        cleaned_terms = [term.strip().lower() for term in terms if term.strip()]
        keywords.extend(cleaned_terms)

    # --- Step 2: Count frequencies ---
    frequency = Counter(keywords)

    # --- Step 3: Write SymSpell dictionary ---
    with open(output_file, 'w', encoding='utf-8') as f:
        for term, freq in frequency.items():
            if '\t' not in term:  # avoid malformed entries
                f.write(f"{term}|{freq}\n")

    print(f"✅ Dictionary written to {output_file}")

if __name__ == "__main__":
    file_path = input("Enter filepath to Excel file: ")
    export_keywords(file_path)
