import json
import configparser
def rename_knobs(input_file, output_file):
    with open(input_file, 'r') as f:
        original_data = json.load(f)

    new_data = {}
    for idx, (old_key, value) in enumerate(original_data.items(), start=1):
        new_key = f"knob{idx}"
        new_data[new_key] = value

    with open(output_file, 'w') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)



config = configparser.ConfigParser()
config.read('./config.ini')
input_file=config['range pruner']['knob_details']
output_file="./range pruner/renamed_knobs"
rename_knobs(
    input_file,
    output_file
)