import cv2
import os
import numpy as np
from PIL import Image
import glob
import argparse

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='CCPD数据集转车牌识别训练数据')
    parser.add_argument('--input', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/det/images", 
                        help='输入图片根目录（需包含train/test/val子目录）')
    parser.add_argument('--output', type=str, default="/drive1/zhd/finalwork/CCPD_dataset/rec", 
                        help='输出车牌图片根目录（会自动创建train/test/val子目录）')
    args = parser.parse_args()

    INPUT_IMG_PATH = args.input
    OUTPUT_REC_PATH = args.output

    # 定义需要的子目录（train/test/val）
    target_subdirs = ['train', 'test', 'val']

    # 蓝牌字符映射表（通用）
    provinces = ["皖", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑", 
                 "苏", "浙", "京", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤", 
                 "桂", "琼", "川", "贵", "云", "藏", "陕", "甘", "青", "宁", 
                 "新", "警", "学", "O"]
    alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 
                 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'O']
    ads = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 
           'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'O']

    # 创建输出根目录及子目录（train/test/val）
    os.makedirs(OUTPUT_REC_PATH, exist_ok=True)
    for subdir in target_subdirs:
        subdir_path = os.path.join(OUTPUT_REC_PATH, subdir)
        os.makedirs(subdir_path, exist_ok=True)

    # 统计变量
    total_num = 0    # 总文件数
    success_num = 0  # 成功数
    error_num = 0    # 错误数

    # 支持更多图片格式
    img_extensions = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']
    img_paths = []
    for ext in img_extensions:
        # 递归查找所有子目录的图片（重点：依赖原图片在train/test/val子目录中）
        img_paths.extend(glob.glob(os.path.join(INPUT_IMG_PATH, "**/*." + ext), recursive=True))

    # 处理每张图片（适配7段式文件名）
    for img_path in img_paths:
        filename = os.path.basename(img_path)
        total_num += 1
        plate_str = ""

        try:
            # 获取原图片所在的父目录（判断是train/test/val）
            # 例如：若img_path是 ".../det/images/train/xxx.jpg"，则parent_dir是"train"
            parent_dir = os.path.basename(os.path.dirname(img_path))
            # 检查父目录是否为目标子目录（train/test/val）
            if parent_dir not in target_subdirs:
                raise ValueError(f"图片所在目录[{parent_dir}]不是有效子目录（需在{target_subdirs}中）")

            # 拆分文件名
            file_parts = filename.split('-')
            if len(file_parts) < 7:
                raise ValueError(f"文件名格式异常，拆分段数={len(file_parts)}（需7段）")
            
            # 7段式CCPD索引对应
            plate_part = file_parts[4]  # plate段索引=4
            box_part = file_parts[2]    # box段索引=2
            
            # 解析plate字符索引（蓝牌7位）
            list_plate = plate_part.split('_')
            # 不足7位补全（避免索引错误）
            list_plate = list_plate[:7] + ['0'] * max(0, 7 - len(list_plate))

            # 解析蓝牌7位字符
            # 第1位：省份
            prov_idx = int(list_plate[0])
            plate_str += provinces[prov_idx] if 0 <= prov_idx < len(provinces) else "京"
            # 第2位：字母
            alpha_idx = int(list_plate[1])
            plate_str += alphabets[alpha_idx] if 0 <= alpha_idx < len(alphabets) else "A"
            # 第3-7位：数字/字母
            for i in range(2, 7):
                char_idx = int(list_plate[i])
                plate_str += ads[char_idx] if 0 <= char_idx < len(ads) else "0"

            # 读取图片（兼容中文路径）
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("图片读取失败（可能损坏或格式不支持）")
            h, w = img.shape[:2]

            # 解析box裁剪坐标
            box = box_part.split('_')
            if len(box) < 2:
                raise ValueError("box段格式错误（需至少2部分）")
            
            pt1 = box[0].split('&')
            pt2 = box[1].split('&')
            if len(pt1) < 2 or len(pt2) < 2:
                raise ValueError("坐标格式错误（需x&y格式）")

            xmin = max(0, int(pt1[0]))
            ymin = max(0, int(pt1[1]))
            xmax = min(w, int(pt2[0]))
            ymax = min(h, int(pt2[1]))

            # 裁剪区域容错
            if (xmax - xmin) < 20 or (ymax - ymin) < 10:
                raise ValueError(f"裁剪区域过小（宽={xmax-xmin}, 高={ymax-ymin}）")

            # 裁剪+Resize为94x24（LPRNet输入）
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img_crop = img_pil.crop((xmin, ymin, xmax, ymax))
            # 适配不同PIL版本的抗锯齿方法
            try:
                img_resize = img_crop.resize((94, 24), Image.Resampling.LANCZOS)
            except AttributeError:
                img_resize = img_crop.resize((94, 24), Image.LANCZOS)
            img_np = np.array(img_resize)

            # 保存路径：输出根目录/子目录（train/test/val）/文件名
            save_name = f"{plate_str}.jpg"
            save_dir = os.path.join(OUTPUT_REC_PATH, parent_dir)  # 对应到train/test/val
            save_path = os.path.join(save_dir, save_name)
            # 避免文件名重复（添加序号）
            if os.path.exists(save_path):
                save_name = f"{plate_str}_{total_num}.jpg"
                save_path = os.path.join(save_dir, save_name)
            # 保存图片（兼容中文路径）
            cv2.imencode('.jpg', cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))[1].tofile(save_path)

            success_num += 1
            print(f"[{total_num}] 成功：{filename} → {os.path.join(parent_dir, save_name)}")

        except ValueError as e:
            print(f"[{total_num}] 跳过：{filename} → {e}")
            error_num += 1
        except IndexError as e:
            print(f"[{total_num}] 跳过：{filename} → 索引越界：{e}")
            error_num += 1
        except Exception as e:
            print(f"[{total_num}] 跳过：{filename} → 未知错误：{str(e)[:80]}")
            error_num += 1
        continue

    # 最终统计
    print("\n===== 7段式蓝牌处理结果 =====")
    print(f"总文件数：{total_num}")
    print(f"成功生成蓝牌图片：{success_num}")
    print(f"跳过/错误数：{error_num}")
    print(f"输出根路径：{OUTPUT_REC_PATH}")
    for subdir in target_subdirs:
        subdir_path = os.path.join(OUTPUT_REC_PATH, subdir)
        # 统计每个子目录的文件数
        subfile_count = len(glob.glob(os.path.join(subdir_path, "*.*")))
        print(f"  {subdir}目录文件数：{subfile_count}")

if __name__ == "__main__":
    main()