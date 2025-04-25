import json

with open('output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('mysql_197.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Create a new dictionary to store the merged result
merged_data = {}

# Traverse the data in the first JSON file
for item in data:
    name = item.get('name')
    if name:
        # If the name exists in config, merge it
        if name in config:
            if config[name].get("type") == "enum": 
                merged_data[name] = {
                "default": config[name].get("default"),
                "dynamic": config[name].get("dynamic"),
                "enum_values": config[name].get("enum_values"),
                "scope": config[name].get("scope"),
                "type": config[name].get("type"),
                "td": item.get('td'),
                "p": item.get('decription'),
                "rank": config[name].get("important_rank")
            }
            else:
                merged_data[name] = {
                    "default": config[name].get("default"),
                    "dynamic": config[name].get("dynamic"),
                    "max": config[name].get("max"),
                    "min": config[name].get("min"),
                    "scope": config[name].get("scope"),
                    "type": config[name].get("type"),
                    "td": item.get('td'),
                    "p": item.get('decription'),
                    "rank": config[name].get("important_rank")
                }

sorted_merged_data = {k: v for k, v in sorted(merged_data.items(), key=lambda item: (item[1].get("rank") is None, item[1].get("rank")))}

with open('candidate_knobs_with_detailed_description.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_merged_data, f, ensure_ascii=False, indent=4)
