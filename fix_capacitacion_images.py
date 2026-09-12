#!/usr/bin/env python3
"""
Copia las imágenes de source/_static/ a source/_extra/capacitacion/img/ y reescribe
los atributos src de los HTML de capacitación para que apunten a ese directorio
local en vez de a las rutas rotas ../../_static/.

source/_extra/capacitacion/img/ NO se versiona: es salida de este script, que corre
como paso previo al build (make images / make html, y build.jobs.pre_build en Read
the Docs).
"""
import os
import re
import shutil
from pathlib import Path

DOCS_DIR = Path(__file__).parent
SOURCE_STATIC = DOCS_DIR / "source" / "_static"
CAP_DIR = DOCS_DIR / "source" / "_extra" / "capacitacion"
IMG_DIR = CAP_DIR / "img"
# El favicon vive en este repo desde que docs se separó de la aplicación.
FAVICON_SRC = SOURCE_STATIC / "favicon.png"

# Matches src=".../_static/(gif/)?filename.ext"
SRC_PATTERN = re.compile(
    r'src="[^"]*/_static/(?:gif/)?([^/"]+\.(gif|png|jpg|jpeg|svg|webp))"',
    re.IGNORECASE,
)


def collect_images():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in SOURCE_STATIC.glob("*.png"):
        shutil.copy2(f, IMG_DIR / f.name)
        count += 1
    gif_dir = SOURCE_STATIC / "gif"
    if gif_dir.exists():
        for f in gif_dir.glob("*.gif"):
            shutil.copy2(f, IMG_DIR / f.name)
            count += 1
    if FAVICON_SRC.exists():
        shutil.copy2(FAVICON_SRC, IMG_DIR / "favicon.png")
        count += 1
    return count


def fix_html_files():
    updated = 0
    for html_file in CAP_DIR.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8")

        rel_img = os.path.relpath(IMG_DIR, html_file.parent).replace(os.sep, "/")

        def replace_src(m):
            return f'src="{rel_img}/{m.group(1)}"'

        new_content = SRC_PATTERN.sub(replace_src, content)

        favicon_tag = f'<link rel="icon" type="image/png" href="{rel_img}/favicon.png">'
        if 'rel="icon"' not in new_content:
            new_content = new_content.replace("</head>", f"    {favicon_tag}\n</head>", 1)

        if new_content != content:
            html_file.write_text(new_content, encoding="utf-8")
            updated += 1
    return updated


if __name__ == "__main__":
    if not SOURCE_STATIC.exists():
        print(f"ERROR: {SOURCE_STATIC} does not exist.")
        raise SystemExit(1)
    img_count = collect_images()
    html_count = fix_html_files()
    print(f"  Copied {img_count} images → {IMG_DIR.relative_to(DOCS_DIR)}")
    print(f"  Updated {html_count} HTML files in {CAP_DIR.relative_to(DOCS_DIR)}")