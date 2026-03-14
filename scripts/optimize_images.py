from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import get_settings
from app.services.image_optimization_service import optimize_images


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Optimize catalog images into WEBP.")
    parser.add_argument("--source", type=Path, default=settings.hejco_images_root)
    parser.add_argument("--output", type=Path, default=settings.hejco_images_root)
    args = parser.parse_args()
    converted = optimize_images(args.source, args.output)
    print(f"converted={converted}")


if __name__ == "__main__":
    main()
