"""Create train/val/test splits without separating byte-identical duplicates."""
import argparse
import hashlib
import os
import random
import shutil
from collections import defaultdict
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
SEED = 42


def is_class_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    classes = [p for p in path.iterdir() if p.is_dir()]
    return len(classes) >= 2 and any(
        any(f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS for f in cls.rglob("*"))
        for cls in classes
    )


def find_source(explicit: str | None = None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_path = os.getenv("PV_DATASET_DIR")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend([
        PROJECT_DIR / "Plant_leave_diseases_dataset_with_augmentation",
        PROJECT_DIR / "dataset" / "raw" / "Plant_leave_diseases_dataset_with_augmentation",
        PROJECT_DIR / "dataset" / "raw",
    ])
    for candidate in candidates:
        candidate = candidate.resolve()
        if is_class_root(candidate):
            return candidate
    tried = "\n".join(f" - {p}" for p in candidates)
    raise FileNotFoundError(
        "Could not find the class-folder dataset. Put "
        "Plant_leave_diseases_dataset_with_augmentation in the project root, "
        "or set PV_DATASET_DIR. Checked:\n" + tried
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Override raw dataset directory")
    parser.add_argument("--output", help="Override processed output directory")
    parser.add_argument("--dry-run", action="store_true", help="Audit and plan without copying files")
    args = parser.parse_args()

    source_dir = find_source(args.source)
    output_dir = Path(args.output or os.getenv("PV_PROCESSED_DIR", str(PROJECT_DIR / "dataset" / "processed"))).expanduser()
    if not output_dir.is_absolute():
        output_dir = (PROJECT_DIR / output_dir).resolve()

    existing_splits = [output_dir / name for name in RATIOS if (output_dir / name).exists()]
    if existing_splits:
        raise FileExistsError(
            "A processed split already exists; refusing to overwrite it. "
            "Choose a new --output path or back up the existing data first: "
            + ", ".join(map(str, existing_splits))
        )

    classes = sorted(p for p in source_dir.iterdir() if p.is_dir())
    if len(classes) != 39:
        print(f"WARNING: expected 39 classes from the supplied checkpoint, found {len(classes)}.")

    # Hash all files and group identical byte streams. Groups are assigned once
    # globally so an exact duplicate cannot cross train/val/test boundaries.
    records = []
    hash_to_records = defaultdict(list)
    for class_index, class_dir in enumerate(classes, start=1):
        images = sorted(p for p in class_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
        print(f"[{class_index}/{len(classes)}] {class_dir.name}: {len(images)} images")
        for path in images:
            digest = sha256(path)
            item = {"class": class_dir.name, "path": path, "digest": digest}
            records.append(item)
            hash_to_records[digest].append(item)

    rng = random.Random(SEED)
    class_totals = {c.name: sum(1 for r in records if r["class"] == c.name) for c in classes}
    class_assigned = {c.name: {split: 0 for split in RATIOS} for c in classes}
    group_split = {}

    # Process each class in deterministic order; if a digest was already
    # assigned by another class, retain that assignment to avoid cross-class leakage.
    for class_dir in classes:
        class_name = class_dir.name
        digests = list(dict.fromkeys(r["digest"] for r in records if r["class"] == class_name))
        rng.shuffle(digests)
        for digest in digests:
            if digest in group_split:
                # This group was already counted when its first class was processed.
                continue
            deficits = {
                split_name: class_totals[class_name] * ratio - class_assigned[class_name][split_name]
                for split_name, ratio in RATIOS.items()
            }
            split = max(deficits, key=deficits.get)
            group_split[digest] = split
            for item in hash_to_records[digest]:
                class_assigned[item["class"]][split] += 1

    split_counts = {split: 0 for split in RATIOS}
    for item in records:
        item["split"] = group_split[item["digest"]]
        split_counts[item["split"]] += 1

    exact_duplicate_groups = sum(1 for group in hash_to_records.values() if len(group) > 1)
    print("\nDataset:", source_dir)
    print("Classes:", len(classes), "Images:", len(records))
    print("Exact duplicate groups:", exact_duplicate_groups)
    print("Planned splits:", split_counts)
    print("NOTE: exact byte-identical duplicates are grouped; augmented near-duplicates are not proven leakage-free.")

    if args.dry_run:
        print("Dry run only; no files copied.")
        return

    for item in records:
        destination_dir = output_dir / item["split"] / item["class"]
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / item["path"].name
        if destination.exists():
            destination = destination_dir / f"{item['path'].stem}_{item['digest'][:10]}{item['path'].suffix}"
        shutil.copy2(item["path"], destination)

    report_path = output_dir / "dataset_report.txt"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("PLANTVILLAGE DATASET SPLIT REPORT\n")
        report.write(f"Source: {source_dir}\nClasses: {len(classes)}\nImages: {len(records)}\n")
        report.write(f"Exact duplicate groups kept in one split: {exact_duplicate_groups}\n")
        report.write(f"Split counts: {split_counts}\n")
        report.write("Caveat: byte-identical duplicates were grouped; perceptual/augmented near-duplicate leakage was not fully tested.\n\n")
        for class_name in sorted(class_totals):
            report.write(f"{class_name}: total={class_totals[class_name]}, " + ", ".join(
                f"{split}={class_assigned[class_name][split]}" for split in RATIOS
            ) + "\n")
    print("Dataset split completed:", output_dir)
    print("Report:", report_path)


if __name__ == "__main__":
    main()
