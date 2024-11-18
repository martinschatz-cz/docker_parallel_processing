# worker_script.py
import os
import json

# Define input and output directories
INPUT_DIR = "/app/data"
OUTPUT_DIR = "/app/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to count words and letters in a file
def count_words_and_letters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    letter_count = sum(1 for char in text if char.isalpha())
    return word_count, letter_count

# Process all .txt files in the input directory
def process_files(input_dir):
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

    for filename in files:
        print(f"Processing file: {filename}")
        file_path = os.path.join(input_dir, filename)
        try:
            word_count, letter_count = count_words_and_letters(file_path)
            results = {"words": word_count, "letters": letter_count}
            
            # Write individual JSON output for each file
            output_file = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=4)
            
            print(f"Results for {filename} written to {output_file}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    process_files(INPUT_DIR)

