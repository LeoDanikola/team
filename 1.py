import os

def parse_elements_from_txt(txt_file_path):
    """
    从一个文本文件中解析出有问题的单元编号。
    文件格式应为 '... element 123 ...'

    Args:
        txt_file_path (str): 包含单元信息 .txt 文件的路径。

    Returns:
        list: 包含所有找到的单元编号的整数列表。
    """
    element_ids = []
    print(f"正在从文件 '{txt_file_path}' 中读取单元编号...")
    try:
        with open(txt_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                words = line.lower().split() # 转为小写并按空格分割
                try:
                    # 查找 'element' 关键字的位置
                    if 'element' in words:
                        idx = words.index('element')
                        # 'element' 后面必须跟一个数字
                        if idx + 1 < len(words):
                            element_id = int(words[idx + 1])
                            element_ids.append(element_id)
                        else:
                            print(f"警告: 第 {line_num} 行找到 'element' 但其后没有编号。")
                except ValueError:
                    # 如果 'element' 后的词不是有效的整数，则忽略
                    print(f"警告: 第 {line_num} 行在 'element' 后找到的不是有效数字。")
                    continue
    except FileNotFoundError:
        print(f"错误: 单元列表文件未找到 -> {txt_file_path}")
        return [] # 返回空列表
        
    # 去重并排序，使其更清晰
    unique_ids = sorted(list(set(element_ids)))
    print(f"从文件中成功读取并去重后共 {len(unique_ids)} 个单元编号。")
    return unique_ids


def remove_elements_from_inp(input_file_path, output_file_path, elements_to_delete):
    """
    从 ABAQUS .inp 文件中删除指定的单元，并从相关的 *ELSET 中移除它们。
    (此函数与之前的版本完全相同)
    
    Args:
        input_file_path (str): 原始 .inp 文件的路径。
        output_file_path (str): 修改后要保存的新 .inp 文件的路径。
        elements_to_delete (list or set): 包含要删除的单元编号的列表或集合。
    """
    elements_to_delete_set = set(elements_to_delete)
    current_block = None
    
    print(f"\n开始处理 .inp 文件: {input_file_path}")
    print(f"共 {len(elements_to_delete_set)} 个单元将被删除。")
    
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
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

1.  **准备文件**：
    * 将上面的代码保存为 `modify_inp_advanced.py`。
    * 准备好您的 `.inp` 文件，例如 `my_model.inp`。
    * 创建一个 `.txt` 文件，例如 `problem_elements.txt`。

    **`problem_elements.txt` 的内容示例**：
    ```
    Error found in element 101 due to high distortion
    Warning: check element 105 for convergence issues
    This is another line with no element info
    High stress concentration at element 230
    element 857
    xxxxx element 1050 XXXX
    element 105   # 重复的编号会被自动处理
    ```

2.  **修改并运行脚本**：
    * 在脚本末尾的 `if __name__ == "__main__":` 部分，设置您自己的三个文件路径。

```python
# ==============================================================================
# ---                             使用示例                             ---
# ==============================================================================
if __name__ == "__main__":
    
    # 1. 设置包含问题单元列表的 TXT 文件
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
