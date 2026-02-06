"""
Crop an image and its YOLO label to keep only the center 60%
(removing 20% from each border).
"""

from PIL import Image
from pathlib import Path


def crop_image_and_labels(image_path, label_path, output_image_path, output_label_path, margin=0.2):
    """
    Crop image to its center region and adjust YOLO labels.

    Args:
        image_path: Path to the source image.
        label_path: Path to the YOLO label file.
        output_image_path: Path to save the cropped image.
        output_label_path: Path to save the adjusted labels.
        margin: Fraction to remove from each border (0.2 = keep center 60%).
    """
    img = Image.open(image_path)
    w, h = img.size

    # Crop boundaries in pixels
    left = int(w * margin)
    top = int(h * margin)
    right = int(w * (1 - margin))
    bottom = int(h * (1 - margin))

    cropped = img.crop((left, top, right, bottom))
    cropped.save(output_image_path)
    print(f"Saved cropped image: {output_image_path}  ({cropped.size[0]}x{cropped.size[1]})")

    # Crop region in normalized coordinates
    crop_x_min = margin
    crop_y_min = margin
    crop_w = 1 - 2 * margin  # 0.6
    crop_h = 1 - 2 * margin  # 0.6

    new_lines = []
    kept = 0
    discarded = 0

    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls = parts[0]
            xc, yc, bw, bh = map(float, parts[1:5])

            # Box edges in original normalized coords
            x1 = xc - bw / 2
            y1 = yc - bh / 2
            x2 = xc + bw / 2
            y2 = yc + bh / 2

            # Clip to crop region
            x1 = max(x1, crop_x_min)
            y1 = max(y1, crop_y_min)
            x2 = min(x2, crop_x_min + crop_w)
            y2 = min(y2, crop_y_min + crop_h)

            # Discard if box has no area after clipping
            if x2 <= x1 or y2 <= y1:
                discarded += 1
                continue

            # Re-normalize to the cropped region [0, 1]
            new_x1 = (x1 - crop_x_min) / crop_w
            new_y1 = (y1 - crop_y_min) / crop_h
            new_x2 = (x2 - crop_x_min) / crop_w
            new_y2 = (y2 - crop_y_min) / crop_h

            new_xc = (new_x1 + new_x2) / 2
            new_yc = (new_y1 + new_y2) / 2
            new_bw = new_x2 - new_x1
            new_bh = new_y2 - new_y1

            new_lines.append(f"{cls} {new_xc} {new_yc} {new_bw} {new_bh}\n")
            kept += 1

    Path(output_label_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_label_path, "w") as f:
        f.writelines(new_lines)

    print(f"Labels: {kept} kept, {discarded} discarded")


if __name__ == "__main__":
    base = Path(r"d:\dev\ia\cours\varroacounter\varroa-counter-large-1")
    stem = "IMG_0234_jpg.rf.90d64baf5c7100e96bc7eb7857d94706"

    image_path = base / "train" / "images" / f"{stem}.jpg"
    label_path = base / "train" / "labels" / f"{stem}.txt"

    output_image_path = base / "train" / "images" / f"{stem}_cropped.jpg"
    output_label_path = base / "train" / "labels" / f"{stem}_cropped.txt"

    crop_image_and_labels(image_path, label_path, output_image_path, output_label_path)
