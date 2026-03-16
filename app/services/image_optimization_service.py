from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterable
from hashlib import sha1
from pathlib import Path

from PIL import Image


def optimize_images(source_dir: Path, output_dir: Path, image_paths: Iterable[Path] | None = None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = tuple(image_paths) if image_paths is not None else tuple(source_dir.iterdir())

    def optimize_image(image_path: Path) -> int:
        if not image_path.is_file() or image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            return 0
        digest = sha1(image_path.name.encode("utf-8")).hexdigest()[:8]
        target = output_dir / f"{image_path.stem}_{digest}.webp"
        if target.exists():
            return 0
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image.save(target, "WEBP", optimize=True, quality=82)
        return 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        return sum(executor.map(optimize_image, paths))
