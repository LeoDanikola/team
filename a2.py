def parse_inp(file_path):
    """
    手动解析 Abaqus .inp 文件以提取节点和单元信息。
    """
    nodes = {}
    elements = {}
    current_keyword = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('**'):
                continue

            if line.startswith('*'):
                current_keyword = line.upper().split(',')[0]
                continue

            if current_keyword == '*NODE':
                parts = [p.strip() for p in line.split(',')]
                node_id = int(parts[0])
                coordinates = [float(p) for p in parts[1:]]
                nodes[node_id] = coordinates
            
            elif current_keyword == '*ELEMENT':
                parts = [p.strip() for p in line.split(',')]
                element_id = int(parts[0])
                connectivity = [int(p) for p in parts[1:]]
                elements[element_id] = connectivity

    return nodes, elements

# 使用示例
inp_file = 'path/to/your/model.inp'
nodes, elements = parse_inp(inp_file)

# 打印节点信息
print("--- Nodes ---")
for node_id, coords in nodes.items():
    print(f"Node ID: {node_id}, Coordinates: {coords}")

# 打印单元信息
print("\n--- Elements ---")
for element_id, connectivity in elements.items():
    print(f"Element ID: {element_id}, Connectivity: {connectivity}")
