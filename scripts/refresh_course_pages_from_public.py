from __future__ import annotations

import re
from pathlib import Path

from generate_site import (
    DOCS_ROOT,
    PUBLIC_RESOURCES,
    TYPE_ORDER,
    Resource,
    extract_docx_text,
    extract_pdf_text,
    extract_pptx_text,
    read_text_file,
    resource_card,
    should_show_course_card,
)


COURSE_PUBLIC_ROOT = PUBLIC_RESOURCES / "courses"
COURSE_DOCS_ROOT = DOCS_ROOT / "resources" / "courses"
TYPE_LABELS = "|".join(re.escape(label) for _, label in TYPE_ORDER)


def course_name_from_page(text: str) -> str:
    match = re.search(r"(?m)^title:\s*(.+)$", text)
    return match.group(1).strip() if match else "课程"


def page_prefix(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    match = re.search(rf"(?m)^## ({TYPE_LABELS})\s*$", text)
    prefix = text[: match.start()].rstrip() if match else text.rstrip()
    return re.sub(r"\n{3,}", "\n\n", prefix)


def resource_text_excerpt(resource: Resource) -> str:
    if resource.ext in {".md", ".txt"}:
        return read_text_file(resource.source)[:20000]
    if resource.ext == ".pptx":
        return extract_pptx_text(resource.source)[:20000]
    if resource.ext == ".docx":
        return extract_docx_text(resource.source)[:20000]
    if resource.ext == ".pdf":
        return extract_pdf_text(resource.source, resource)[:20000]
    return ""


def load_course_resources(course_slug: str, course_name: str) -> dict[str, list[Resource]]:
    by_module: dict[str, list[Resource]] = {label: [] for _, label in TYPE_ORDER}
    course_dir = COURSE_PUBLIC_ROOT / course_slug
    for module_slug, module_label in TYPE_ORDER:
        module_dir = course_dir / module_slug
        if not module_dir.exists():
            continue
        for path in sorted(p for p in module_dir.iterdir() if p.is_file()):
            rel = f"resources/courses/{course_slug}/{module_slug}/{path.name}"
            resource = Resource(
                source=path,
                rel=f"{course_slug}/{module_slug}/{path.name}",
                name=path.name,
                ext=path.suffix.lower(),
                size=path.stat().st_size,
                sha256="",
                area="course",
                course_slug=course_slug,
                course_name=course_name,
                module_slug=module_slug,
                module_label=module_label,
                included=True,
                dest_rel=rel,
            )
            resource.text_excerpt = resource_text_excerpt(resource)
            by_module[module_label].append(resource)
    return by_module


def refresh_page(page: Path) -> bool:
    course_slug = page.parent.name
    if not (COURSE_PUBLIC_ROOT / course_slug).exists():
        return False

    original = read_text_file(page).replace("\r\n", "\n").replace("\r", "\n")
    course_name = course_name_from_page(original)
    by_module = load_course_resources(course_slug, course_name)

    lines = [page_prefix(original), ""]
    for _, label in TYPE_ORDER:
        raw_items = by_module.get(label, [])
        visible = [item for item in raw_items if should_show_course_card(item, raw_items)]
        if not visible:
            continue
        lines.extend([f"## {label}", "", '<div class="resource-grid">'])
        lines.extend(resource_card(item, index) for index, item in enumerate(visible, 1))
        lines.extend(["</div>", ""])

    page.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    rewritten = 0
    for page in sorted(COURSE_DOCS_ROOT.glob("*/index.md")):
        if refresh_page(page):
            rewritten += 1
    print(f"Refreshed {rewritten} course pages from {COURSE_PUBLIC_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
