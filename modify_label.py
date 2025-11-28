import glob
import os

label_dir = r"D:\lab\final-lab\CCPD_dataset\det\labels\val"
label_files = glob.glob(os.path.join(label_dir, "*.txt"))

print("Found", len(label_files), "label files.")

for file in label_files:
    with open(file, "r") as f:
        lines = f.read().strip().splitlines()

    new_lines = []
    for line in lines:
        if line.strip() == "":
            continue

        items = line.split()

        # 修正 class id（比如 0.0 → 0）
        try:
            cls = int(float(items[0]))  # 转成整数
            items[0] = str(cls)
        except:
            print("无法解析 class id:", items[0], "in file:", file)

        new_lines.append(" ".join(items))

    with open(file, "w") as f:
        f.write("\n".join(new_lines))

print("All labels fixed!")
