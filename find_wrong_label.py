import glob
import os

label_dir = "/drive1/zhd/finalwork/CCPD_dataset/det/labels"

label_files = glob.glob(label_dir + "/**/*.txt", recursive=True)

print(f"共发现 {len(label_files)} 个 label 文件\n")

def check_float_list(parts):
    """检查能否转成浮点数"""
    try:
        _ = [float(x) for x in parts]
        return True
    except:
        return False

error_found = False

for f in label_files:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()

    for idx, line in enumerate(lines):
        raw = line.rstrip("\n")

        # 1. 空行
        if raw.strip() == "":
            print(f"[空行] {f} (line {idx+1}) : {repr(raw)}")
            error_found = True
            continue

        # 消除 BOM
        raw = raw.replace("\ufeff", "")

        parts = raw.split()

        # 2. 列数不为 5
        if len(parts) != 5:
            print(f"[列数错误] {f} (line {idx+1}) -> {parts}")
            error_found = True
            continue

        # 3. 不能转换为 float
        if not check_float_list(parts):
            print(f"[转换失败] {f} (line {idx+1}) -> {parts}")
            error_found = True
            continue

if not error_found:
    print("所有 label 文件都正常，没有发现格式问题。")
else:
    print("\n️ 检查完成，以上是有问题的 label 文件。")
