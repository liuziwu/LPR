"""
@Author: HuKai
@Date: 2022/5/29  10:47
@github: https://github.com/HuKai97
"""
import os
import cv2
import argparse

def txt_translate(img_dir, label_dir):
    """
    将CCPD格式转换为YOLOv5标签格式
    :param img_dir: 图像文件目录
    :param label_dir: 标签文件输出目录
    """
    # 创建标签目录（如果不存在）
    os.makedirs(label_dir, exist_ok=True)
    
    # 支持的图片格式
    img_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    for filename in os.listdir(img_dir):
        # 跳过非图片文件
        ext = os.path.splitext(filename)[1]
        if ext not in img_extensions:
            print(f"跳过非图片文件：{filename}")
            continue
            
        try:
            # 解析文件名获取边界框
            # 格式示例：xxx-xxx-lx&ly_rx&ry-xxx.jpg
            parts = filename.split("-", 3)  # 分割为[前缀, 前缀, lx&ly_rx&ry, 后缀]
            if len(parts) < 3:
                raise ValueError(f"文件名格式错误，无法解析边界框：{filename}")
                
            bbox_part = parts[2]
            lt_str, rb_str = bbox_part.split("_", 1)  # 分割为左上角和右下角
            lx, ly = lt_str.split("&", 1)  # 左上角坐标
            rx, ry = rb_str.split("&", 1)  # 右下角坐标
            
            # 读取图片获取尺寸
            img_path = os.path.join(img_dir, filename)
            img = cv2.imread(img_path)
            if img is None:
                raise IOError("图片无法读取（可能损坏）")
            img_h, img_w = img.shape[:2]
            
            # 计算YOLO格式坐标（归一化）
            lx, ly, rx, ry = map(int, [lx, ly, rx, ry])
            width = rx - lx
            height = ry - ly
            cx = lx + width / 2
            cy = ly + height / 2
            
            # 归一化（避免除零错误）
            if img_w == 0 or img_h == 0:
                raise ValueError("图片尺寸异常（宽或高为0）")
            cx_norm = cx / img_w
            cy_norm = cy / img_h
            w_norm = width / img_w
            h_norm = height / img_h
            
            # 保存标签文件（保留6位小数）
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(label_dir, f"{base_name}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                # 绿牌是第0类，蓝牌是第1类（保持原分类）
                f.write(f"0 {cx_norm:.6f} {cy_norm:.6f} {w_norm:.6f} {h_norm:.6f}\n")
                
            print(f"处理完成：{filename} → {os.path.basename(txt_path)}")
            
        except (IndexError, ValueError, IOError) as e:
            print(f"处理失败 {filename}：{str(e)}")
        except Exception as e:
            print(f"处理异常 {filename}：{str(e)}")

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='CCPD数据集转YOLOv5标签格式')
    parser.add_argument('--train-img', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/images/train/",
                        help='训练集图像目录')
    parser.add_argument('--val-img', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/images/val/",
                        help='验证集图像目录')
    parser.add_argument('--test-img', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/images/test/",
                        help='测试集图像目录')
    parser.add_argument('--train-label', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/labels/train/",
                        help='训练集标签输出目录')
    parser.add_argument('--val-label', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/labels/val/",
                        help='验证集标签输出目录')
    parser.add_argument('--test-label', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/labels/test/",
                        help='测试集标签输出目录')
    args = parser.parse_args()

    # 处理各数据集
    txt_translate(args.train_img, args.train_label)
    txt_translate(args.val_img, args.val_label)
    txt_translate(args.test_img, args.test_label)