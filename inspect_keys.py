import json
import os

def inspect_first_record():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'missionaries.json')
    
    if not os.path.exists(file_path):
        print("❌ missionaries.json not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find the list
    items = []
    if isinstance(data, list): items = data
    elif isinstance(data, dict):
        for key in ['rows', 'items', 'missionaries', 'data']:
            if key in data:
                items = data[key]
                break
    
    if len(items) > 0:
        print("--- RAW DATA FOR 1 MISSIONARY ---")
        # Print the keys and values of the first person nicely
        first_person = items[0]
        for key, value in first_person.items():
            print(f"{key}: {value}")
    else:
        print("❌ Could not find any missionary records inside the file.")

if __name__ == "__main__":
    inspect_first_record()