import os

def parse_elements_from_txt(txt_file_path):
    """
    从一个特定格式的文本文件中解析出有问题的单元编号。
    新格式的特征是：
    1. 以 'distorted ter' 作为数据块的起始标志。
    2. 之后有一个空行和两行表头。
    3. 数据行格式为 'name.1823 ...'。
    4. 数据块以一个空行结束。

    Args:
        txt_file_path (str): 包含单元信息 .txt 文件的路径。

    Returns:
        list: 包含所有找到的单元编号的整数列表。
    """
    element_ids = []
    # 设置一个状态标志，用于指示是否找到了数据块的起始位置
    found_start_marker = False
    
    print(f"正在从文件 '{txt_file_path}' 中按新格式读取单元编号...")
    try:
        with open(txt_file_path, 'r') as f:
            for line in f:
                # --- 状态1: 搜索起始标志 'distorted ter' ---
                if not found_start_marker:
                    if 'distorted ter' in line:
                        print("找到起始标志 'distorted ter'。")
                        found_start_marker = True
                        # 根据描述，标志后面有一个空行和两个表头，共3行需要跳过
                        try:
                            next(f) # 跳过空行
                            next(f) # 跳过表头1
                            next(f) # 跳过表头2
                            print("已跳过空行和表头，开始读取单元数据...")
                        except StopIteration:
                            # 如果文件在表头处就结束了，则中断
                            break
                    continue # 继续搜索下一行

                # --- 状态2: 读取并解析数据行 ---
                
                # 如果是空行，说明数据表结束
                if not line.strip():
                    print("检测到空行，单元数据读取结束。")
                    break
                
                # 解析数据行
                words = line.split()
                if not words: # 如果是空行（再次检查）
                    continue

                # 第一个词应该是 'name.单元号'
                first_word = words[0]
                if first_word.startswith('name.'):
                    try:
                        # 分割 'name.' 和数字
                        element_id = int(first_word.split('.')[1])
                        element_ids.append(element_id)
                    except (ValueError, IndexError):
                        # 如果'.'后面不是数字或格式错误，则忽略这行
                        print(f"警告: 无法从 '{first_word}' 中解析单元编号，已跳过此行。")
                        continue

    except FileNotFoundError:
        print(f"错误: 单元列表文件未找到 -> {txt_file_path}")
        return []

    # 去重并排序
    unique_ids = sorted(list(set(element_ids)))
    print(f"从文件中成功读取并去重后共 {len(unique_ids)} 个单元编号。")
    return unique_ids


def remove_elements_from_inp(input_file_path, output_file_path, elements_to_delete):
    """
    从 ABAQUS .inp 文件中删除指定的单元，并从相关的 *ELSET 中移除它们。
    (此函数与之前的版本完全相同，无需改动)
    """
    elements_to_delete_set = set(elements_to_delete)
    current_block = None
    
    print(f"\n开始处理 .inp 文件: {input_file_path}")
    print(f"共 {len(elements_to_delete_set)} 个单元将被删除。")
    
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            # (此部分代码与之前完全相同)
            for line in infile:
                stripped_line = line.strip()

                if stripped_line.startswith('*'):
                    main_keyword = stripped_line.split(',')[0].upper()
                    current_block = main_keyword
                    outfile.write(line)
                    continue

                if stripped_line.startswith('**') or not stripped_line:
                    outfile.write(line)
                    continue

                if current_block == '*ELEMENT':
                    try:
                        element_id = int(stripped_line.split(',')[0])
                        if element_id in elements_to_delete_set:
                            continue 
                        else:
                            outfile.write(line)
                    except (ValueError, IndexError):
                        outfile.write(line)
                
                elif current_block == '*ELSET':
                    original_elements = [int(e) for e in stripped_line.replace(',', ' ').split() if e.isdigit()]
                    kept_elements = [e for e in original_elements if e not in elements_to_delete_set]
                    if kept_elements:
                        formatted_lines = []
                        for i in range(0, len(kept_elements), 16):
                            chunk = kept_elements[i:i+16]
                            formatted_lines.append(", ".join(map(str, chunk)))
                        outfile.write("\n".join(formatted_lines) + "\n")
                else:
                    outfile.write(line)
    except FileNotFoundError:
        print(f"错误: 输入文件未找到 -> {input_file_path}")
        return

    print("-" * 50)
    print(f"处理完成！已生成新文件: {output_file_path}")


### 如何使用

您的使用方法和之前完全一样，脚本已经足够智能，可以处理新的文件格式。

1.  **准备文件**：
    * 将上面的代码保存为 `modify_inp_new_format.py`。
    * 准备好您的 `.inp` 文件。
    * 准备好您的新格式的 `.txt` 文件。

    **新格式 `problem_elements.txt` 的内容示例**：
    ```
    这里是文件开头的一堆无关内容
    可以是很多行
    ...
    ...
    distorted ter

    Element Table Header Line 1
    Element Table Header Line 2
    name.1823 0.23 8.63 102.36 182.2 yes
    name.1824 0.25 8.71 103.11 183.9 yes
    name.2001 0.19 9.12 105.78 190.1 no
    name.2015 0.22 8.66 102.95 182.5 yes
    
    这里是表格结尾的空行，标志着数据结束
    后面也可能有一堆无关内容
    ...
    ```

2.  **修改并运行脚本**：
    * 在脚本末尾的 `if __name__ == "__main__":` 部分，设置您自己的三个文件路径。

```python
# ==============================================================================
# ---                             使用示例                             ---
# ==============================================================================
if __name__ == "__main__":
    
    # 1. 设置包含问题单元列表的 TXT 文件 (新格式)
    PROBLEM_TXT_FILE = 'path/to/your/problem_elements.txt'
    
    # 2. 设置输入和输出的 .inp 文件路径
    INPUT_INP_FILE = 'path/to/your/original_model.inp'
    OUTPUT_INP_FILE = 'path/to/your/modified_model.inp'
    
    # 3. 从 TXT 文件中解析出要删除的单元列表
    problematic_elements = parse_elements_from_txt(PROBLEM_TXT_FILE)
    
    # 4. 确保我们成功读取到了单元并且 .inp 文件存在
    if problematic_elements and os.path.exists(INPUT_INP_FILE):
        # 执行核心的修改和写入功能
        remove_elements_from_inp(INPUT_INP_FILE, OUTPUT_INP_FILE, problematic_elements)
    elif not problematic_elements:
        print("\n未能从 TXT 文件中读取到任何有效的单元编号，程序终止。")
    else:
        print(f"\n错误：输入文件 '{INPUT_INP_FILE}' 不存在，程序终止。")
