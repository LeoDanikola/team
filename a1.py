from abaqus_parser import read_inp

# 读取 .inp 文件
inp_file = 'path/to/your/model.inp'
model = read_inp(inp_file)

# --- 提取节点信息 ---
print("--- Nodes ---")
if 'NODE' in model:
    for node in model['NODE']:
        node_id = node[0]
        coordinates = node[1:]
        print(f"Node ID: {node_id}, Coordinates: {coordinates}")

# --- 提取单元信息 ---
print("\n--- Elements ---")
if 'ELEMENT' in model:
    # 单元类型通常在关键字行中指定
    element_type = model['ELEMENT'][0]['options'].get('TYPE', 'Unknown')
    print(f"Element Type: {element_type}")
    for element in model['ELEMENT']:
        element_id = element['data'][0]
        connectivity = element['data'][1:]
        print(f"Element ID: {element_id}, Connectivity: {connectivity}")

# --- 提取集合信息 ---
print("\n--- Node Sets ---")
if 'NSET' in model:
    for nset in model['NSET']:
        set_name = nset['options'].get('NSET', 'Unnamed')
        node_ids = nset['data']
        print(f"Node Set: {set_name}, Nodes: {node_ids}")

print("\n--- Element Sets ---")
if 'ELSET' in model:
    for elset in model['ELSET']:
        set_name = elset['options'].get('ELSET', 'Unnamed')
        element_ids = elset['data']
        print(f"Element Set: {set_name}, Elements: {element_ids}")
