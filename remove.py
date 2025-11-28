import os
import shutil
import random
from tqdm import tqdm  # 用于显示进度条（可选）

# -------------------------- 配置参数 --------------------------
# 源图片目录（请确保路径正确）
source_dir = "/drive1/zhd/finalwork/CCPD_dataset/CCPD2019/ccpd_base"
# 目标目录根路径
target_root = "/drive1/zhd/finalwork/CCPD_dataset/det/images"
# 训练集比例（0.8表示80%）
train_ratio = 0.8
# 支持的图片格式（可根据需要添加）
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
# 是否打乱文件顺序（确保分割随机性）
shuffle = True
# --------------------------------------------------------------

def split_and_copy_images():
    # 1. 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误：源目录不存在 -> {source_dir}")
        return
    
    # 2. 创建目标目录结构（train/val）
    train_dir = os.path.join(target_root, "train")
    val_dir = os.path.join(target_root, "val")
    for dir_path in [train_dir, val_dir]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"确保目标目录存在：{dir_path}")
    
    # 3. 获取源目录下所有图片文件
    image_files = []
    for filename in os.listdir(source_dir):
        # 过滤出图片文件
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(source_dir, filename)
            # 确保是文件（不是子目录）
            if os.path.isfile(file_path):
                image_files.append(filename)
    
    # 检查是否有图片文件
    if not image_files:
        print(f"警告：源目录中没有找到图片文件 -> {source_dir}")
        print(f"支持的图片格式：{image_extensions}")
        return
    
    total_count = len(image_files)
    print(f"\n找到 {total_count} 张图片，开始按 {train_ratio:.0%}/{1-train_ratio:.0%} 分割...")
    
    # 4. 打乱文件顺序（确保分割的随机性）
    if shuffle:
        random.seed(42)  # 设置随机种子，保证结果可复现（可选）
        random.shuffle(image_files)
    
    # 5. 计算分割点
    train_count = int(total_count * train_ratio)
    train_files = image_files[:train_count]
    val_files = image_files[train_count:]
    
    print(f"训练集：{len(train_files)} 张图片")
    print(f"验证集：{len(val_files)} 张图片")
    
    # 6. 复制图片到训练集目录
    print("\n正在复制训练集图片...")
    for filename in tqdm(train_files, desc="训练集复制进度"):
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(train_dir, filename)
        # 使用copy2保留文件元数据（也可以用copy）
        shutil.copy2(src_path, dst_path)
    
    # 7. 复制图片到验证集目录
    print("\n正在复制验证集图片...")
    for filename in tqdm(val_files, desc="验证集复制进度"):
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(val_dir, filename)
        shutil.copy2(src_path, dst_path)
    
    print("\n✅ 图片分割和复制完成！")
    print(f"训练集路径：{train_dir}")
    print(f"验证集路径：{val_dir}")

if __name__ == "__main__":
    # 可选：安装tqdm（用于进度条显示）
    try:
        from tqdm import tqdm
    except ImportError:
        print("提示：安装tqdm可以显示复制进度条 -> pip install tqdm")
        # 定义一个简单的进度条替代
        class tqdm:
            def __init__(self, iterable, desc="进度"):
                self.iterable = iterable
                self.desc = desc
                self.total = len(iterable)
                self.count = 0
            
            def __iter__(self):
                for item in self.iterable:
                    self.count += 1
                    if self.count % 50 == 0:  # 每50个文件显示一次进度
                        print(f"{self.desc}：{self.count}/{self.total}")
                    yield item
    
    split_and_copy_images()