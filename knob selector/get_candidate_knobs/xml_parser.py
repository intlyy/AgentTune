import re
import json
from lxml import etree

# Read XML file
with open('official_doc.xml', 'r', encoding='utf-8') as f:
    xml_data = f.read()

# Using lxml parser to parse XML data
parser = etree.XMLParser(recover=True)
root = etree.fromstring(xml_data, parser=parser)

# parse each listitem
def parse_listitem(listitem):
    th_content = None
    td_content = None
    p_content = []
    first_a_name = None

    # Traverse all sub elements of the listitem
    for elem in listitem.iter():
        if elem.tag == 'a' and 'name' in elem.attrib and first_a_name is None:
            first_a_name = elem.attrib['name']


    # Extract all<p>tag content
    table_found = False
    for elem in listitem:
        if elem.tag == 'div':
            table_found = True  

        elif table_found and elem.tag == 'p':
            if elem.text:
                p_str = ''.join(elem.itertext())  
                p_str_no_lable = re.sub(r'<[^>]*>', '', p_str)  
                p_str_no_newline = re.sub('\n', '', p_str_no_lable)  
                p_str_no_overspace = re.sub(r'\s{2,}', ' ', p_str_no_newline) 
                p_content.append(p_str_no_overspace.strip())

    if table_found == False:
        for elem in listitem:
            if elem.tag == 'a':
                table_found = True  

            elif table_found and elem.tag == 'p':
                if elem.text:
                    p_str = ''.join(elem.itertext())  
                    p_str_no_lable = re.sub(r'<[^>]*>', '', p_str)  
                    p_str_no_newline = re.sub('\n', '', p_str_no_lable)  
                    p_str_no_overspace = re.sub(r'\s{2,}', ' ', p_str_no_newline) 
                    p_content.append(p_str_no_overspace.strip())

    return first_a_name, th_content, td_content, ' '.join(p_content)

i = 0
data = []

for listitem in root.findall('.//li[@class="listitem"]'):
    first_a_name, th_content, td_content, p_content = parse_listitem(listitem)
    item = {}
    if first_a_name:
        i += 1
        item['name'] = first_a_name
    if p_content:
        item['decription'] = p_content
    if item:
        data.append(item)

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(i)
