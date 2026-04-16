import os
import shutil
import random
from pathlib import Path

# ================= CONFIG =================
IMG_SRC = r"D:\Plastic_Waste_Detection\Dataset\New folder"
LBL_SRC = r"D:\Plastic_Waste_Detection\Dataset\New folder"

OUTPUT_BASE = r"D:\Plastic_Waste_Detection\Dataset\final"

TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

RANDOM_SEED = 42
# ==========================================

random.seed(RANDOM_SEED)


def create_dirs(base_path):
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(base_path, "images", split), exist_ok=True)
        os.makedirs(os.path.join(base_path, "labels", split), exist_ok=True)


def get_image_files(img_dir):
    exts = [".jpg", ".jpeg", ".png"]
    return [
        f for f in os.listdir(img_dir)
        if Path(f).suffix.lower() in exts
    ]


def split_dataset(files):
    random.shuffle(files)

    total = len(files)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_files = files[:train_end]
    val_files = files[train_end:val_end]
    test_files = files[val_end:]

    return train_files, val_files, test_files


def copy_files(files, split, img_src, lbl_src, out_base):
    for file in files:
        img_src_path = os.path.join(img_src, file)
        lbl_name = Path(file).stem + ".txt"
        lbl_src_path = os.path.join(lbl_src, lbl_name)

        img_dst = os.path.join(out_base, "images", split, file)
        shutil.copy(img_src_path, img_dst)

        # Copy label only if exists (plastic images)
        if os.path.exists(lbl_src_path):
            lbl_dst = os.path.join(out_base, "labels", split, lbl_name)
            shutil.copy(lbl_src_path, lbl_dst)
        else:
            print(f"ℹ️ Non-plastic: {file}")


def main():
    print("🚀 Preparing dataset (train/val/test)...")

    # STEP 1: Create folder structure
    create_dirs(OUTPUT_BASE)

    # STEP 2: Load images
    images = get_image_files(IMG_SRC)
    print(f"📦 Total images: {len(images)}")

    # STEP 3: Split dataset
    train_files, val_files, test_files = split_dataset(images)

    print(f"✅ Train: {len(train_files)}")
    print(f"✅ Val: {len(val_files)}")
    print(f"✅ Test: {len(test_files)}")

    # STEP 4: Copy files
    copy_files(train_files, "train", IMG_SRC, LBL_SRC, OUTPUT_BASE)
    copy_files(val_files, "val", IMG_SRC, LBL_SRC, OUTPUT_BASE)
    copy_files(test_files, "test", IMG_SRC, LBL_SRC, OUTPUT_BASE)

    print("🎯 Dataset ready with train/val/test split!")


if __name__ == "__main__":
    main()