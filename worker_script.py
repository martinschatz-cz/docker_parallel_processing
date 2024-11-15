# worker_script.py
import os
import json
import hashlib

INPUT_DIR = "/app/data"
OUTPUT_DIR = "/app/output"
REPLICA_ID = os.getenv("REPLICA_ID")  # Use a unique ID for each replica
os.makedirs(OUTPUT_DIR, exist_ok=True)

def count_words_and_letters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    letter_count = sum(1 for char in text if char.isalpha())
    return word_count, letter_count

def process_files(input_dir):
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    
    # Filter files for this replica only
    assigned_files = [f for f in files if int(hashlib.md5(f.encode()).hexdigest(), 16) % REPLICA_COUNT == REPLICA_ID]

    results = {}
    for filename in assigned_files:
        file_path = os.path.join(input_dir, filename)
        word_count, letter_count = count_words_and_letters(file_path)
        results[filename] = {"words": word_count, "letters": letter_count}

    output_file = os.path.join(OUTPUT_DIR, f"results_{REPLICA_ID}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Replica {REPLICA_ID} processed files. Results saved to {output_file}")

if __name__ == "__main__":
    REPLICA_COUNT = int(os.getenv("REPLICA_COUNT", 1))
    REPLICA_ID = int(os.getenv("REPLICA_ID", 0))
    process_files(INPUT_DIR)

