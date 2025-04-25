from flask import Flask, request, jsonify
from openai import OpenAI
import json
import re
import os,sys
import heapq
from config_rank import sort_list
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')

file_path = config['workload analyzer']['output_file']
with open(file_path, "r") as f:
    workload_features = f.read().strip()  
database_kernel=config['knob selector']['database_kernel']
hardware=config['knob selector']['hardware']

knob_list_path = config['range pruner']['output_file']
with open(knob_list_path,"r") as f:
    knobs = json.load(f) 
knobs = json.dumps(knobs, indent=4)

metric_path = config['configuration recommender']['metric_file']
with open(metric_path, "r") as f:
    inner_metrics = f.read().strip() 

db_metric=config['configuration recommender']['db_metric']


def extract_key_value_pairs(json_string):
    # match "key": value 
    pattern = re.compile(r'"(\w+)":\s*([\d.]+)')
    matches = pattern.findall(json_string)
    data = {key: int(value) for key, value in matches}
    return data

def convert_to_bytes(value):
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    match = re.match(r'(\d+)([KMGT]B)', value)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        return number * units[unit]
    return int(value)

def replace_units(json_string):
    def replace_match(match):
        return str(convert_to_bytes(match.group(0)))
    
    json_string = re.sub(r'\d+[KMGT]B', replace_match, json_string)
    return json_string


def remove_comments(json_string):
    json_string = re.sub(r'//.*', '', json_string)
    json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)
    json_string = re.sub(r',\s*}', '}', json_string)
    json_string = re.sub(r',\s*]', ']', json_string)
    return json_string

def call_open_source_llm(model, messages,filename):

    client = OpenAI(
        api_key="", 
        base_url=""
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 1,
        top_p = 0.98
    )

    for choice in completion.choices:

        pattern = r'\{[^{}]+\}'
        match = re.search(pattern, choice.message.content, re.DOTALL)

        if match:
            json_str = match.group(0)
            json_str = replace_units(json_str)
            config_dict = extract_key_value_pairs(json_str)
            #json_str = remove_comments(json_str)
            #config_dict = json.loads(json_str)
            print(config_dict)
            if not config_dict:
                return
            config_dict = json.dumps(config_dict)
            with open(filename, 'r') as f:
                data_str = f.read()

            # Split the data into individual JSON strings
            json_strings = data_str.strip().split('\n')

            # # Prepare the final structured JSON format
            # for json_str in json_strings:
            #     d = json.loads(json_str)
            if config_dict in json_strings :
                return
            with open(filename, 'a') as f:
                print("sucess recommendation!")
                f.write('\n')
                f.write(config_dict)

        else:
            print("No JSON configuration found in the input.")

history_top = []
app = Flask(__name__)
request_count = 0
@app.route('/process', methods=['POST'])
def process_data():


    global request_count
    global history_top
    request_count += 1
    filename = f'./configuration recommender/record/turn_{request_count}'
    file = open(filename, 'w')
    file.close()

    data = request.get_json()
    for item in data:
        last_knobs = item.get('knob')
        throughput = item.get('throughput')
        now_inner_metrics = item.get('metric')

        last_knobs = json.dumps(last_knobs, indent=4)
        now_inner_metrics = json.dumps(now_inner_metrics, indent=4)

        print(last_knobs)
        print(now_inner_metrics)
        print(throughput)

        if len(history_top) < config['configuration recommender']['history_num']:
            # If the queue is not full, join directly
            heapq.heappush(history_top, (throughput, item))
        else:
            # update the queue
            heapq.heappushpop(history_top, (throughput, item))

        if throughput == 0 :
            throughput = "0, because database starting failed under current configuration"
        
        sorted_history = sorted(history_top, key=lambda x: -x[0])  
        # Sort by performance
        history_entries = []
        for idx, (t, item) in enumerate(sorted_history, 1):
            knob_str = json.dumps(item['knob'], indent=4)
            metric_str = json.dumps(item['metric'], indent=4)
            history_entries.append(
                f"Task {idx}:\n"
                f"Throughput: {t}\n"
                f"Knob Configuration:\n{knob_str}\n"
                f"Metrics:\n{metric_str}\n"
            )
        
        messages1 = [
        {
            "role": "system",
            "content": """
                You are an experienced database administrators, skilled in database knob tuning.
            """
        },
        {
            "role": "user",
            "content": """
                Task Overview: 
                Recommend optimal knob configuration based on the inner metrics and workload characteristics in order to optimize the {db_metric} metric.
                knobs:{knob}
                Workload and Database information: 
                - Workload Features: {workload_features}
                - Database Kernel: {database_kernel}
                - Hardware: {hardware}
                Historical Knob Tuning Tasks:
                {history}
                Current Configuration:
                {last_knob}
                Database Feedback:
                - Performance : {performance} 
                - Inner Metrics: {now_inner_metric}
                Output Format:
                Strictly utilize the aforementioned knobs, ensuring that the generated configuration are formatted as follows:
                {{
                    "knob": value, 
                    ……
                }}
                Now, let's think step by step.

            """.format(knob=knobs, inner_metric=inner_metrics, last_knob = last_knobs, now_inner_metric = now_inner_metrics, performance = throughput, db_metric = db_metric,history="\n\n".join(history_entries), workload_features=workload_features, database_kernel=database_kernel, hardware=hardware)
        }
        ]

        model = config['configuration recommender']['model']

        global last_result
        while i<config['configuration recommender']['node_count'] :
            i = i+1
            call_open_source_llm(model, messages1, filename)
    
    with open(filename, 'r') as f:
        data_str = f.read()
        check = data_str.strip()  
        if not check:  
            print("File is empty")
            data_str = last_result
    
    with open(filename, 'r') as f:
        data_str = f.read()
        # Split the data into individual JSON strings
        json_strings = data_str.strip().split('\n')
    
    top_k = sort_list(json_strings)
    with open('./configuration recommender/record/top_k', 'a') as f:
        json.dump(top_k, f, indent=4)
        f.close()
    


    # send the result to DB_client 
    return jsonify(top_k)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['configuration recommender']['LLM_server_port'])

