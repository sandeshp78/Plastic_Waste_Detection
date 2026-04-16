# # 1. Import the library
# from inference_sdk import InferenceHTTPClient

# # 2. Connect to your workflow
# client = InferenceHTTPClient(
#     api_url="https://serverless.roboflow.com",
#     api_key="6FlVXFmKILg9Gysou4PO"
# )

# # 3. Run your workflow on an image
# result = client.run_workflow(
#     workspace_name="tobis-workspace-afqsq",
#     workflow_id="detect-and-classify-3",
#     images={
#         "image": "D:\\Plastic_Waste_Detection\\Dataset\\labeled\d2\\0010_a02b01c2d3e0f1g0h0_jpg.rf.IT7H1pk6wBznWZ1onEoV.jpg" # Path to your image file
#     },
#     use_cache=True # Speeds up repeated requests
# )

# # 4. Get your results
# print(result)

# import random
# from pathlib import Path

# dataset_path = Path(r"D:\Plastic_Waste_Detection\Dataset\New folder")

# files = [f for f in dataset_path.glob("*") if "plastic" not in f.name.lower()]

# random.shuffle(files)

# # keep only 400
# for f in files[400:]:
#     f.unlink()


# import os
# from pathlib import Path

# dataset_path = Path(r"D:\Plastic_Waste_Detection\Dataset\New folder")

# count = 0

# for img_file in dataset_path.rglob("*.*"):
#     if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
#         if "plastic" not in img_file.name.lower():
#             count += 1

# print("Non-plastic images:", count)

# cnt = 0
# for img_file in dataset_path.rglob("*.*"):
#     if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
#         if "plastic"  in img_file.name.lower():
#             cnt += 1

# print("plastic images:", cnt)




# checking class Imbalancing 
# from collections import Counter
# from pathlib import Path

# label_path = Path("Dataset/final/labels/train")

# counter = Counter()

# for file in label_path.glob("*.txt"):
#     with open(file) as f:
#         for line in f:
#             cls = int(line.split()[0])
#             counter[cls] += 1

# print(counter)




# from pathlib import Path

# label_dir = Path(r"D:\Plastic_Waste_Detection\Dataset\final\labels")

# for txt_file in label_dir.rglob("*.txt"):
#     new_lines = []

#     with open(txt_file, "r") as f:
#         for line in f:
#             parts = line.strip().split()

#             if len(parts) == 5:   # safety check
#                 parts[0] = "0"

#             new_lines.append(" ".join(parts))

#     with open(txt_file, "w") as f:
#         f.write("\n".join(new_lines))



# from pathlib import Path

# label_dir = Path("Dataset/final/labels")

# wrong = 0

# for txt_file in label_dir.rglob("*.txt"):
#     with open(txt_file) as f:
#         for line in f:
#             if not line.startswith("0"):
#                 print(f"❌ Found non-zero class in: {txt_file}")
#                 wrong += 1

# print("\n===================")
# print(f"Wrong labels found: {wrong}")
# print("===================")

# from collections import Counter
# from pathlib import Path

# counter = Counter()
# label_path = Path("Dataset/final/labels/train")

# for file in label_path.glob("*.txt"):
#     with open(file) as f:
#         for line in f:
#             cls = int(line.split()[0])
#             counter[cls] += 1

# print(counter)