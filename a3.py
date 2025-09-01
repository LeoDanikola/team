from abaqus import *
from abaqusConstants import *
import inpParser

# .inp 文件的路径
inp_file_name = 'path/to/your/model.inp'

# 解析 .inp 文件
my_model_inp = inpParser.InputFile(fileName=inp_file_name)

# 遍历并打印文件中的所有关键字
for keyword in my_model_inp.keywords:
    print(keyword.name)
    # 可以进一步处理每个关键字的数据
    # for data_line in keyword.data:
    #     print(data_line)

# 示例：提取并打印所有节点
node_keyword = my_model_inp.findKeyword('*NODE')
if node_keyword:
    print("\n--- Nodes ---")
    for node_data in node_keyword.data:
        print(f"Node ID: {node_data[0]}, Coordinates: {node_data[1:]}")

# 示例：提取并打印所有单元
element_keyword = my_model_inp.findKeyword('*ELEMENT')
if element_keyword:
    print("\n--- Elements ---")
    element_type = element_keyword.getOptions().get('TYPE', 'Unknown')
    print(f"Element Type: {element_type}")
    for element_data in element_keyword.data:
        print(f"Element ID: {element_data[0]}, Connectivity: {element_data[1:]}")
