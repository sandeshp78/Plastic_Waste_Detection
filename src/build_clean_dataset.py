import csv
import hashlib
import random
import shutil
from pathlib import Path

import cv2
import numpy as np


RANDOM_SEED = 42
SPLIT_RATIOS = {
    "train": 0.75,
    "val": 0.15,
    "test": 0.10,
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MIN_MASK_COMPONENT_AREA = 25


def project_root():
    return Path(__file__).resolve().parent.parent


def source_dirs(root):
    return [
        root / "Dataset" / "New folder",
        root / "Dataset" / "RGB and RGNIR Plastic Waste Database" / "RGB images with annotations",
    ]


def dataset2_paths(root):
    base = root / "Dataset2"
    return {
        "base": base,
        "images": base / "Raw_Images",
        "masks": base / "Segmentation_Masks",
        "labels": base / "Image_labels_Binary Classification Task.csv",
    }


def original_group_key(path):
    stem = path.stem
    for marker in ("_jpg.rf.", "_jpeg.rf.", "_png.rf."):
        if marker in stem:
            return stem.split(marker, 1)[0]
    return stem


def file_hash(path):
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_label(label_path):
    if not label_path.exists():
        return []

    cleaned_lines = []
    for line in label_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue

        try:
            _, x_center, y_center, width, height = map(float, parts)
        except ValueError:
            continue

        if not all(0 <= value <= 1 for value in [x_center, y_center, width, height]):
            continue
        if width <= 0 or height <= 0:
            continue

        cleaned_lines.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return cleaned_lines


def mask_to_yolo_boxes(mask_path):
    if not mask_path.exists():
        return []

    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return []

    height, width = mask.shape[:2]
    binary_mask = (mask > 0).astype(np.uint8)
    component_count, _, stats, _ = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)

    boxes = []
    for component_index in range(1, component_count):
        x, y, box_width, box_height, area = stats[component_index]
        if area < MIN_MASK_COMPONENT_AREA:
            continue

        x_center = (x + box_width / 2) / width
        y_center = (y + box_height / 2) / height
        norm_width = box_width / width
        norm_height = box_height / height
        boxes.append(f"0 {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}")

    return boxes


def collect_samples(root):
    samples = []
    seen_hashes = set()

    for source_dir in source_dirs(root):
        if not source_dir.exists():
            print(f"[WARN] Source folder missing: {source_dir}")
            continue

        for image_path in source_dir.iterdir():
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            image_hash = file_hash(image_path)
            if image_hash in seen_hashes:
                continue
            seen_hashes.add(image_hash)

            label_path = image_path.with_suffix(".txt")
            samples.append(
                {
                    "image_path": image_path,
                    "label_lines": read_label(label_path),
                    "group_key": f"{source_dir.name}_{original_group_key(image_path)}",
                }
            )

    paths = dataset2_paths(root)
    if paths["images"].exists() and paths["masks"].exists() and paths["labels"].exists():
        with paths["labels"].open(newline="", encoding="utf-8") as handle:
            label_rows = {
                row["image name"].strip(): row["Presence of plastic waste?"].strip().lower()
                for row in csv.DictReader(handle)
            }

        for image_path in paths["images"].iterdir():
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            image_hash = file_hash(image_path)
            if image_hash in seen_hashes:
                continue
            seen_hashes.add(image_hash)

            is_positive = label_rows.get(image_path.name) == "yes"
            mask_path = paths["masks"] / f"{image_path.stem}_mask.png"
            label_lines = mask_to_yolo_boxes(mask_path) if is_positive else []

            samples.append(
                {
                    "image_path": image_path,
                    "label_lines": label_lines,
                    "group_key": f"Dataset2_{original_group_key(image_path)}",
                }
            )

    return samples


def split_groups(samples):
    grouped = {}
    for sample in samples:
        grouped.setdefault(sample["group_key"], []).append(sample)

    group_keys = list(grouped)
    random.Random(RANDOM_SEED).shuffle(group_keys)

    total = len(group_keys)
    train_end = int(total * SPLIT_RATIOS["train"])
    val_end = train_end + int(total * SPLIT_RATIOS["val"])

    split_by_group = {}
    for group_key in group_keys[:train_end]:
        split_by_group[group_key] = "train"
    for group_key in group_keys[train_end:val_end]:
        split_by_group[group_key] = "val"
    for group_key in group_keys[val_end:]:
        split_by_group[group_key] = "test"

    return split_by_group


def reset_output_dirs(output_dir):
    if output_dir.exists():
        shutil.rmtree(output_dir)

    for split in SPLIT_RATIOS:
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def copy_samples(samples, split_by_group, output_dir):
    summary = {
        split: {"images": 0, "labeled_images": 0, "negative_images": 0, "boxes": 0}
        for split in SPLIT_RATIOS
    }

    for index, sample in enumerate(samples, start=1):
        split = split_by_group[sample["group_key"]]
        src_image = sample["image_path"]
        dst_name = f"{index:05d}_{src_image.name}"
        dst_image = output_dir / "images" / split / dst_name
        dst_label = output_dir / "labels" / split / f"{Path(dst_name).stem}.txt"

        shutil.copy2(src_image, dst_image)
        if sample["label_lines"]:
            dst_label.write_text("\n".join(sample["label_lines"]) + "\n", encoding="utf-8")
        else:
            dst_label.write_text("", encoding="utf-8")

        summary[split]["images"] += 1
        summary[split]["boxes"] += len(sample["label_lines"])
        if sample["label_lines"]:
            summary[split]["labeled_images"] += 1
        else:
            summary[split]["negative_images"] += 1

    return summary


def write_data_yaml(output_dir):
    data_yaml = output_dir / "data.yaml"
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {output_dir.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "",
                "names:",
                "  0: plastic",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main():
    root = project_root()
    output_dir = root / "Dataset" / "robot_clean"

    print("[INFO] Building clean RGB plastic dataset...")
    samples = collect_samples(root)
    if not samples:
        print("[ERROR] No images found.")
        return

    split_by_group = split_groups(samples)
    reset_output_dirs(output_dir)
    summary = copy_samples(samples, split_by_group, output_dir)
    write_data_yaml(output_dir)

    print(f"[SUCCESS] Clean dataset created at: {output_dir}")
    for split, stats in summary.items():
        print(
            f"[INFO] {split}: {stats['images']} images, "
            f"{stats['labeled_images']} labeled, "
            f"{stats['negative_images']} negative, "
            f"{stats['boxes']} boxes"
        )


if __name__ == "__main__":
    main()
