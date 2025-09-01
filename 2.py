import os

def remove_elements_from_inp(input_file_path, output_file_path, elements_to_delete):
    """
    从 ABAQUS .inp 文件中删除指定的单元，并从相关的 *ELSET 中移除它们。

    Args:
        input_file_path (str): 原始 .inp 文件的路径。
        output_file_path (str): 修改后要保存的新 .inp 文件的路径。
        elements_to_delete (list or set): 包含要删除的单元编号的列表或集合。
    """
    # 使用集合(set)可以极大地提高查找效率 (O(1) 平均时间复杂度)
    elements_to_delete_set = set(elements_to_delete)
    
    # 状态变量，用于跟踪当前正在处理的 .inp 文件块
    current_block = None
    
    print(f"开始处理文件: {input_file_path}")
    print(f"共 {len(elements_to_delete_set)} 个单元将被删除。")
    
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            for line in infile:
                stripped_line = line.strip()

                # 1. 处理关键字行 (以 '*' 开头)
                if stripped_line.startswith('*'):
                    # 提取主关键字，忽略参数 (例如, 从 '*ELEMENT, TYPE=C3D8R' 提取 '*ELEMENT')
                    main_keyword = stripped_line.split(',')[0].upper()
                    current_block = main_keyword
                    outfile.write(line)
                    continue

                # 2. 处理注释行或空行 (以 '**' 开头或为空)
                if stripped_line.startswith('**') or not stripped_line:
                    outfile.write(line)
                    continue

                # 3. 根据当前块处理数据行
                # --- 删除单元定义 ---
                if current_block == '*ELEMENT':
                    try:
                        # 单元数据行的第一个值是单元编号
                        element_id = int(stripped_line.split(',')[0])
                        if element_id in elements_to_delete_set:
                            # 如果单元ID在删除列表中，则跳过此行（不写入输出文件）
                            continue 
                        else:
                            outfile.write(line)
                    except (ValueError, IndexError):
                        # 如果行格式不正确，直接写入
                        outfile.write(line)
                
                # --- 从单元集 (ELSET) 中移除单元 ---
                elif current_block == '*ELSET':
                    # 读取该行所有的单元号
                    # .replace(',', ' ') 是为了处理行尾可能存在的逗号
                    original_elements = [int(e) for e in stripped_line.replace(',', ' ').split() if e.isdigit()]
                    
                    # 过滤掉需要删除的单元
                    kept_elements = [e for e in original_elements if e not in elements_to_delete_set]
                    
                    if kept_elements:
                        # Abaqus 通常每行最多16个ID，这里我们以此格式化输出
                        formatted_lines = []
                        for i in range(0, len(kept_elements), 16):
                            chunk = kept_elements[i:i+16]
                            # 将ID转换为字符串并用逗号连接
                            formatted_lines.append(", ".join(map(str, chunk)))
                        
                        # 写入格式化后的行
                        outfile.write("\n".join(formatted_lines) + "\n")

                # --- 对于所有其他块，原样写入 ---
                else:
                    outfile.write(line)

    except FileNotFoundError:
        print(f"错误: 输入文件未找到 -> {input_file_path}")
        return

    print("-" * 50)
    print(f"处理完成！已生成新文件: {output_file_path}")


### 如何使用

1.  **准备工作**：
    * 将上面的 Python 代码保存为一个文件，例如 `modify_inp.py`。
    * 准备好您的 `.inp` 文件，例如 `my_model.inp`。
    * 获取您需要删除的单元编号列表。

2.  **修改并运行脚本**：
    * 在脚本的末尾添加以下代码来调用函数。
    * 修改 `INPUT_INP_FILE`、`OUTPUT_INP_FILE` 和 `PROBLEMATIC_ELEMENTS` 这三个变量的值。

```python
# ==============================================================================
# ---                             使用示例                             ---
# ==============================================================================
if __name__ == "__main__":
    
    # 1. 设置输入和输出文件的路径
    INPUT_INP_FILE = 'path/to/your/original_model.inp'
    OUTPUT_INP_FILE = 'path/to/your/modified_model.inp'
    
    # 2. 定义一个包含所有有问题单元编号的列表
    #    这些编号将被从模型中彻底删除
    PROBLEMATIC_ELEMENTS = [101, 105, 230, 857, 1050] 
    
    # 检查输入文件是否存在
    if not os.path.exists(INPUT_INP_FILE):
        print(f"错误：输入文件 '{INPUT_INP_FILE}' 不存在。请检查路径。")
    else:
        # 3. 执行函数
        remove_elements_from_inp(INPUT_INP_FILE, OUTPUT_INP_FILE, PROBLEMATIC_ELEMENTS)

