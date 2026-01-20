import json
import os
from datetime import datetime

def load_json_file(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', filename)
    if not os.path.exists(file_path): return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date(date_str):
    """ Tries to make IMOS dates look nice (YYYY-MM-DD) """
    if not date_str: return ""
    try:
        # Takes '2024-07-24' and keeps it.
        return date_str.split("T")[0]
    except:
        return date_str

def get_master_roster():
    raw_data = load_json_file('missionaries.json')
    clean_roster = []
    # ... (Keep your existing list finding logic) ...
    for m in missionary_list:
        # ... (Keep your existing filtering logic) ...
        clean_roster.append({
            "ID": m.get('missionaryId'), # HIDDEN IDENTIFIER
            "Status": "Staying", 
            "Training": False,   
            "Missionary": f"{m.get('preferredLastName', '').strip()}, {m.get('preferredFirstName', '').strip()}",
            "Zone": m.get('zone', ''),
            "Area": m.get('area', ''),
            "Title": m.get('missTypeCode', '').title(),
            "Email": m.get('email', ''),
            "Arrival": m.get('assignmentStartDate', '').split('T')[0] if m.get('assignmentStartDate') else '',
            "Departure": m.get('assignmentEndDate', '').split('T')[0] if m.get('assignmentEndDate') else ''
        })
    return clean_roster

if __name__ == "__main__":
    roster = get_master_roster()
    print(f"✅ Filtered Roster Count: {len(roster)}")
    if len(roster) > 0:
        print("Sample Row:", roster[0])

def get_area_list():
    """ Parses areas.json to get a clean list for dropdowns """
    raw_data = load_json_file('areas.json')
    area_names = set()

    area_list = []
    if isinstance(raw_data, list): area_list = raw_data
    elif isinstance(raw_data, dict):
        for key in ['rows', 'items', 'areas', 'data']:
            if key in raw_data:
                area_list = raw_data[key]
                break

    for a in area_list:
        try:
            name = a.get('name')
            if name: area_names.add(name)
        except: continue
        
    return sorted(list(area_names))