import os
from pathlib import Path
DATASET_PATH = r"D:\Plastic_Waste_Detection\Dataset\final"

image_dir = Path(DATASET_PATH) / "images"
label_dir = Path(DATASET_PATH) / "labels"

errors = 0

def check_split(split):
    global errors

    img_path = image_dir / split
    lbl_path = label_dir / split

    print(f"\n🔍 Checking {split}...")

    for img_file in img_path.glob("*.*"):
        if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        label_file = lbl_path / (img_file.stem + ".txt")

        # Case 1: Missing label (plastic images should have)
        if not label_file.exists():
            print(f"⚠️ No label (might be non-plastic): {img_file.name}")
            continue

        with open(label_file, "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            print(f"❌ Empty label file: {label_file.name}")
            errors += 1
            continue

        for line in lines:
            parts = line.strip().split()

            # Case 2: Wrong format
            if len(parts) != 5:
                print(f"❌ Wrong format: {label_file.name}")
                errors += 1
                continue

            class_id, x, y, w, h = parts

            # Case 3: Invalid class id
            if not class_id.isdigit():
                print(f"❌ Invalid class ID: {label_file.name}")
                errors += 1

            # Case 4: Values out of range
            for val in [x, y, w, h]:
                try:
                    v = float(val)
                    if v < 0 or v > 1:
                        print(f"❌ Out of range value: {label_file.name}")
                        errors += 1
                except:
                    print(f"❌ Non-numeric value: {label_file.name}")
                    errors += 1


for split in ["train", "val", "test"]:
    check_split(split)

print("\n========================")
print(f"Total Errors Found: {errors}")
print("========================")



# ============================================ Deleting Empty label imgs ====================================================
# import os
# from pathlib import Path

# DATASET_PATH = Path(r"D:\Plastic_Waste_Detection\Dataset\final")

# image_dirs = [
#     DATASET_PATH / "images" / "train",
#     DATASET_PATH / "images" / "val",
#     DATASET_PATH / "images" / "test"
# ]

# label_dirs = [
#     DATASET_PATH / "labels" / "train",
#     DATASET_PATH / "labels" / "val",
#     DATASET_PATH / "labels" / "test"
# ]

# deleted = 0

# for img_dir, lbl_dir in zip(image_dirs, label_dirs):

#     print(f"\n🔍 Checking {img_dir.name}...")

#     for img_file in img_dir.glob("*.*"):
#         if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
#             continue

#         label_file = lbl_dir / (img_file.stem + ".txt")

#         # 🔥 ONLY delete if it's a PLASTIC image without label
#         if not label_file.exists():
#             if "plastic" in img_file.name.lower():
#                 print(f"❌ Removing bad plastic image: {img_file.name}")
#                 img_file.unlink()
#                 deleted += 1
#             else:
#                 print(f"ℹ️ Keeping non-plastic: {img_file.name}")

# print("\n====================")
# print(f"Deleted plastic images: {deleted}")










# ================================= Deleting Wrong formate files imgs ========================================================
# from pathlib import Path

# DATASET_PATH = Path(r"D:\Plastic_Waste_Detection\Dataset\final")

# label_dirs = [
#     DATASET_PATH / "labels" / "train",
#     DATASET_PATH / "labels" / "val",
#     DATASET_PATH / "labels" / "test"
# ]

# image_dirs = [
#     DATASET_PATH / "images" / "train",
#     DATASET_PATH / "images" / "val",
#     DATASET_PATH / "images" / "test"
# ]

# deleted = 0

# for lbl_dir, img_dir in zip(label_dirs, image_dirs):

#     print(f"\n🔍 Checking {lbl_dir.name}...")

#     for txt_file in lbl_dir.glob("*.txt"):

#         with open(txt_file, "r") as f:
#             lines = f.readlines()

#         is_wrong = False

#         for line in lines:
#             parts = line.strip().split()

#             # YOLO format must have exactly 5 values
#             if len(parts) != 5:
#                 is_wrong = True
#                 break

#         if is_wrong:
#             print(f"❌ Deleting wrong label: {txt_file.name}")

#             # Delete label
#             txt_file.unlink()

#             # Delete corresponding image
#             img_file = img_dir / (txt_file.stem + ".jpg")

#             if img_file.exists():
#                 print(f"❌ Deleting image: {img_file.name}")
#                 img_file.unlink()

#             deleted += 1

# print("\n====================")
# print(f"Deleted wrong format files: {deleted}")
# print("====================")
# print("====================")