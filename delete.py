import os
from matplotlib import pyplot as plt
import random

folder = "/drive1/zhd/finalwork/CCPD_dataset/CCPD2019/ccpd_base"  # 替换为你的路径
files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".jpg")]

# 随机取 4 万个文件
# to_delete = random.sample(files, 49000)
#
for f in files:
    os.remove(f)
# for i in range(1000):
#     os.rename(files[i],files[i].replace("test","train"))

print("删除完成，共删掉：", len(files), "张")
