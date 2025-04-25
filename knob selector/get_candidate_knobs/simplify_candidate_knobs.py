import json
import re

def extract_first_sentence(text):
    match = re.match(r'([^.]*[.])', text)
    if match:
        return match.group(1)
    else:
        return text 

with open('candidate_knobs_with_detailed_description.json', 'r', encoding='utf-8') as f:
    data = json.load(f)



clean_data = {}

for name in data.keys():
    if data[name].get("type") == "enum": 
        clean_data[name] = {
        "enum_values": data[name].get("enum_values"),
        "type": data[name].get("type"),
        "description":extract_first_sentence(data[name].get('p')),
    }
    else:
        clean_data[name] = {
            "max": data[name].get("max"),
            "min": data[name].get("min"),
            "type": data[name].get("type"),
            "description": extract_first_sentence(data[name].get('p')),
        }

with open('100_mysql_one_OLAP.json', 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=4)
