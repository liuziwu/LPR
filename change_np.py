import os
import re

# 需要替换的目录，改成你的项目路径
project_dir = "/drive1/zhd/finalwork"

# 定义替换规则
replacements = {
    r'\bnp\.int\b': 'int',
    r'\bnp\.float\b': 'float',
    r'\bnp\.bool\b': 'bool',
    r'\bnp\.complex\b': 'complex',
    r'\bnp\.object\b': 'object',
    r'\bnp\.str\b': 'str',
}

# 遍历项目目录下的所有 .py 文件
for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            original_content = content
            # 执行替换
            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)
            # 如果有变化，写回文件
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated: {file_path}")

print("替换完成！")
