from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (REPO_ROOT.parent / "控制分享资料").resolve()
BASE_PATH = "/CSE_Learning_Resource_Hub"
PUBLIC_RESOURCES = REPO_ROOT / "public" / "resources"
DOCS_ROOT = REPO_ROOT / "src" / "content" / "docs"
REPORTS_ROOT = REPO_ROOT / "reports"

TYPE_ORDER = [
    ("course-guide", "课程导读"),
    ("lecture-notes", "课堂笔记"),
    ("review-outline", "复习提纲"),
    ("open-book-a4", "半开卷 A4"),
    ("past-materials", "历年资料"),
    ("memory-exams", "回忆卷"),
    ("lab-materials", "实验资料"),
    ("assignments", "作业与习题"),
    ("code-simulation", "代码与仿真"),
    ("other-materials", "其他资料"),
]
TYPE_LABEL_TO_SLUG = {label: slug for slug, label in TYPE_ORDER}

OTHER_CATEGORIES = [
    ("cet6", "六级"),
    ("interview", "面试"),
    ("postgraduate", "升学"),
    ("employment", "就业"),
    ("postgraduate-exam", "考研"),
    ("competition", "竞赛"),
    ("tools-and-methods", "工具与方法"),
    ("other", "其他"),
]

LEARNING_MAJORS = [
    ("automation", "自动化"),
    ("robotics", "机器人工程"),
]

SEMESTER_ORDER = [
    ("sophomore-fall", "大二上"),
    ("sophomore-spring", "大二下"),
    ("junior-fall", "大三上"),
    ("junior-spring", "大三下"),
]

KNOWN_COURSES = [
    ("circuit-and-analog-electronics-lab", "电路与模拟电子技术实验", [r"模电.*实验", r"电路与模拟电子技术实验", r"仿真实验报告"]),
    ("circuit-and-analog-electronics", "电路与模拟电子技术", [r"模电", r"模拟电子", r"电路与模拟电子"]),
    ("robotics-ii", "机器人学 II", [r"机器人学\s*(II|Ⅱ|2)", r"Robotics2"]),
    ("robotics-i", "机器人学 I", [r"机器人学\s*(I|Ⅰ|1)", r"\brobotics\b"]),
    ("robot-sensing-technology", "机器人传感技术", [r"机器人传感"]),
    ("intro-to-robotics-and-ai", "机器人导论（机器人与人工智能导论）", [r"机器人导论", r"机器人与人工智能导论"]),
    ("automatic-control-principles-b", "自动控制理论（乙）", [r"自控乙", r"自动控制理论.*乙", r"自动控制原理.*乙"]),
    ("signals-and-systems", "信号与系统", [r"信号与系统"]),
    ("complex-functions", "复变函数", [r"复变函数", r"拉普拉斯变换"]),
    ("artificial-intelligence-and-machine-learning", "人工智能与机器学习", [r"人工智能与机器学习", r"人机复习", r"AI-ML"]),
    ("data-structures", "数据结构", [r"数据结构"]),
    ("probability-and-mathematical-statistics", "概率论和数理统计", [r"概率论", r"数理统计"]),
    ("operations-research", "运筹学", [r"运筹学"]),
    ("control-theory", "控制论", [r"控制论"]),
    ("theoretical-mechanics", "理论力学", [r"理论力学"]),
]

TEXT_EXTENSIONS = {".md", ".txt"}
ATTACHMENT_EXTENSIONS = {".pdf", ".docx", ".pptx", ".zip", ".jpg", ".jpeg", ".png", ".agx", ".mo", ".ms14"}
LARGE_LIMIT = 50 * 1024 * 1024
HARD_LIMIT = 100 * 1024 * 1024
PRIVACY_ALLOWLIST = {
    "复变函数/复变函数/Stein答案1.pdf": "人工确认可公开",
    "机器人学II_复习提纲.pdf": "人工确认可公开；“二维码”为课程内容语境",
}


@dataclass
class Resource:
    source: Path
    rel: str
    name: str
    ext: str
    size: int
    sha256: str
    area: str
    course_slug: str = ""
    course_name: str = ""
    module_slug: str = ""
    module_label: str = ""
    topic_slug: str = ""
    topic_label: str = ""
    included: bool = False
    dest_rel: str = ""
    notes: list[str] = field(default_factory=list)
    privacy_hits: list[str] = field(default_factory=list)

    @property
    def public_url(self) -> str:
        return f"{BASE_PATH}/{self.dest_rel.replace(os.sep, '/')}" if self.dest_rel else ""

    @property
    def size_label(self) -> str:
        return human_size(self.size)


def human_size(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def md_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def slugify_ascii(text: str, fallback: str) -> str:
    text = text.lower()
    replacements = {
        "a4": "a4",
        "pdf": "pdf",
        "docx": "docx",
        "pptx": "pptx",
        "机器人": "robot",
        "机器人学": "robotics",
        "复习": "review",
        "提纲": "outline",
        "笔记": "notes",
        "回忆": "memory",
        "试卷": "exam",
        "期末": "final",
        "答案": "answers",
        "模电": "analog-electronics",
        "电路": "circuit",
        "自控": "automatic-control",
        "信号": "signals",
        "系统": "systems",
        "复变": "complex-functions",
        "概率": "probability",
        "运筹": "operations-research",
        "理论力学": "theoretical-mechanics",
        "控制论": "control-theory",
        "主题": "topic",
        "第一章": "chapter-1",
        "第二章": "chapter-2",
        "第三章": "chapter-3",
        "第四章": "chapter-4",
        "第五章": "chapter-5",
        "第六章": "chapter-6",
        "第七章": "chapter-7",
        "第八章": "chapter-8",
        "第九章": "chapter-9",
        "第10章": "chapter-10",
    }
    for zh, en in replacements.items():
        text = text.replace(zh, f" {en} ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text or fallback


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.startswith("word/") and n.endswith(".xml")]
            chunks: list[str] = []
            for name in names:
                if not name.endswith(("document.xml", "footnotes.xml", "endnotes.xml")):
                    continue
                root = ET.fromstring(zf.read(name))
                chunks.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
            return "\n".join(chunks)
    except Exception:
        return ""


def extract_pptx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            names = sorted(n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
            chunks: list[str] = []
            for name in names:
                root = ET.fromstring(zf.read(name))
                chunks.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
            return "\n".join(chunks)
    except Exception:
        return ""


def extract_pdf_text(path: Path, resource: Resource) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-q", str(path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=45,
        )
        if completed.returncode != 0:
            resource.notes.append("未能自动检查 PDF 内容")
            return ""
        return completed.stdout.decode("utf-8", errors="replace")
    except Exception:
        resource.notes.append("未能自动检查 PDF 内容")
        return ""


def scan_text_for_privacy(text: str, filename: str) -> list[str]:
    hits: list[str] = []
    combined = f"{filename}\n{text}"
    checks = [
        ("邮箱", re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)),
        ("手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
        ("身份证号", re.compile(r"(?<!\d)[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)")),
        ("二维码或群号", re.compile(r"(二维码|QQ群|微信群|群号|加群|班级群)")),
        ("教师个人联系方式", re.compile(r"(教师|老师).{0,12}(手机号|电话|微信|邮箱)", re.S)),
    ]
    for label, pattern in checks:
        if pattern.search(combined):
            hits.append(label)
    if re.search(r"(学号|student\s*id).{0,10}\d{8,12}", combined, re.I | re.S):
        hits.append("学号")
    if re.search(r"(详细住址|宿舍地址|家庭住址).{0,30}[\u4e00-\u9fff]{2,}", combined):
        hits.append("详细住址")
    return sorted(set(hits))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_course(text: str) -> tuple[str, str]:
    for slug, name, patterns in KNOWN_COURSES:
        if any(re.search(pattern, text, re.I) for pattern in patterns):
            return slug, name
    return "", ""


def infer_module(text: str, ext: str) -> tuple[str, str]:
    if re.search(r"(A4|半开卷)", text, re.I):
        return TYPE_LABEL_TO_SLUG["半开卷 A4"], "半开卷 A4"
    if re.search(r"(回忆卷|回忆版|期末回忆|memory)", text, re.I):
        return TYPE_LABEL_TO_SLUG["回忆卷"], "回忆卷"
    if re.search(r"(期末卷|历年|模拟卷|试题|试卷|参考20\d{2})", text, re.I):
        return TYPE_LABEL_TO_SLUG["历年资料"], "历年资料"
    if re.search(r"(复习|提纲|知识点|整理|自测)", text, re.I):
        return TYPE_LABEL_TO_SLUG["复习提纲"], "复习提纲"
    if re.search(r"(实验|仿真)", text, re.I):
        if ext in {".mo", ".agx", ".ms14"}:
            return TYPE_LABEL_TO_SLUG["代码与仿真"], "代码与仿真"
        return TYPE_LABEL_TO_SLUG["实验资料"], "实验资料"
    if re.search(r"(作业|习题|答案|课后|小测)", text, re.I):
        return TYPE_LABEL_TO_SLUG["作业与习题"], "作业与习题"
    if re.search(r"(笔记|主题|lecture|notes|robotics\.pdf)", text, re.I):
        return TYPE_LABEL_TO_SLUG["课堂笔记"], "课堂笔记"
    if ext in {".mo", ".agx", ".ms14"}:
        return TYPE_LABEL_TO_SLUG["代码与仿真"], "代码与仿真"
    return TYPE_LABEL_TO_SLUG["其他资料"], "其他资料"


def infer_experience(path: Path, rel: str) -> tuple[str, str, str]:
    text = rel + " " + path.name
    if re.search(r"(六级|CET-?6|英语)", text, re.I):
        return "other", "cet6", "六级"
    if re.search(r"(面经|面试)", text):
        if re.search(r"(PhD|港科|升学|保研|直博|提前批)", text, re.I):
            return "other", "postgraduate", "升学"
        return "other", "interview", "面试"
    if re.search(r"(考研)", text, re.I):
        return "other", "postgraduate-exam", "考研"
    if re.search(r"(升学|保研|直博|PhD|港科)", text, re.I):
        return "other", "postgraduate", "升学"
    if re.search(r"(就业|实习|求职)", text):
        return "other", "employment", "就业"
    if re.search(r"(竞赛|比赛)", text):
        return "other", "competition", "竞赛"
    if re.search(r"(github|工具|方法|链接|开源)", text, re.I):
        return "other", "tools-and-methods", "工具与方法"
    if re.search(r"(大二|大三|学习经验|经验分享|上课体验|避坑|备考经验)", text):
        return "learning", "study-experience", "学习经验"
    return "", "", ""


def infer_learning_semester(resource: Resource) -> tuple[str, str]:
    text = f"{resource.rel} {resource.name}"
    if "大二上" in text:
        return "sophomore-fall", "大二上"
    if "大二下" in text:
        return "sophomore-spring", "大二下"
    if "大三上" in text:
        return "junior-fall", "大三上"
    if "大三下" in text:
        return "junior-spring", "大三下"
    return "other", "其他"


def classify(path: Path, sha: str) -> Resource:
    rel = path.relative_to(SOURCE_ROOT).as_posix()
    ext = path.suffix.lower()
    size = path.stat().st_size
    r = Resource(path, rel, path.name, ext, size, sha, area="pending")
    path_text = rel.replace("/", " ")

    exp_area, topic_slug, topic_label = infer_experience(path, rel)
    course_slug, course_name = infer_course(path_text)

    if exp_area and (path.parent == SOURCE_ROOT or ext in TEXT_EXTENSIONS):
        r.area = exp_area
        r.topic_slug = topic_slug
        r.topic_label = topic_label
        return r

    if course_slug:
        r.area = "course"
        r.course_slug = course_slug
        r.course_name = course_name
        module_slug, module_label = infer_module(path_text, ext)
        r.module_slug = module_slug
        r.module_label = module_label
        return r

    r.area = "pending"
    r.topic_slug = "uncategorized"
    r.topic_label = "待分类资料"
    r.module_slug = TYPE_LABEL_TO_SLUG["其他资料"]
    r.module_label = "其他资料"
    return r


def resource_dest(resource: Resource, seen_dest_names: set[str]) -> str:
    stem = slugify_ascii(Path(resource.name).stem, f"resource-{resource.sha256[:10]}")
    if len(stem) > 72:
        stem = stem[:72].strip("-")
    suffix = resource.ext.lower()
    file_name = f"{stem}-{resource.sha256[:8]}{suffix}"
    while file_name in seen_dest_names:
        file_name = f"{stem}-{resource.sha256[:12]}{suffix}"
    seen_dest_names.add(file_name)

    if resource.area == "course":
        return f"resources/courses/{resource.course_slug}/{resource.module_slug}/{file_name}"
    if resource.area == "learning":
        return f"resources/experiences/learning/{resource.topic_slug}/{file_name}"
    if resource.area == "other":
        return f"resources/experiences/other/{resource.topic_slug}/{file_name}"
    return f"resources/pending/uncategorized/{file_name}"


def clean_markdown(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"\[b\](.*?)\[/b\]", r"**\1**", text, flags=re.I | re.S)
    text = re.sub(r"\[/?(?:color|size|font)[^\]]*\]", "", text, flags=re.I)
    text = re.sub(r"(?<![\]\)])(https?://[^\s<>\)]+)", r"[\1](\1)", text)
    text = re.sub(r"\n{4,}", "\n\n", text)
    return text.strip() + "\n"


def page_slug_for_resource(resource: Resource) -> str:
    return slugify_ascii(Path(resource.name).stem, f"note-{resource.sha256[:10]}")[:80].strip("-") or f"note-{resource.sha256[:10]}"


def ensure_clean_generated_dirs() -> None:
    for path in [
        PUBLIC_RESOURCES,
        DOCS_ROOT / "resources" / "courses",
        DOCS_ROOT / "resources" / "pending",
        DOCS_ROOT / "experiences" / "learning",
        DOCS_ROOT / "experiences" / "other",
        DOCS_ROOT / "internal",
    ]:
        if path.exists():
            shutil.rmtree(path)
    PUBLIC_RESOURCES.mkdir(parents=True, exist_ok=True)
    (DOCS_ROOT / "resources").mkdir(parents=True, exist_ok=True)
    (DOCS_ROOT / "experiences" / "learning").mkdir(parents=True, exist_ok=True)
    (DOCS_ROOT / "experiences" / "other").mkdir(parents=True, exist_ok=True)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)


def privacy_scan(resource: Resource) -> None:
    text = ""
    if resource.ext in TEXT_EXTENSIONS:
        text = read_text_file(resource.source)
    elif resource.ext == ".docx":
        text = extract_docx_text(resource.source)
        if not text:
            resource.notes.append("未能自动检查 Word 内容")
    elif resource.ext == ".pptx":
        text = extract_pptx_text(resource.source)
        if not text:
            resource.notes.append("未能自动检查 PPT 内容")
    elif resource.ext == ".pdf":
        text = extract_pdf_text(resource.source, resource)
    elif resource.ext in {".jpg", ".jpeg", ".png"}:
        resource.notes.append("图片内容未自动检查")
    elif resource.ext not in ATTACHMENT_EXTENSIONS:
        resource.notes.append("未知格式，按附件处理")

    resource.privacy_hits = scan_text_for_privacy(text[:1_000_000], resource.name)
    if resource.rel in PRIVACY_ALLOWLIST and resource.privacy_hits:
        resource.notes.append(f"隐私规则命中已人工放行：{PRIVACY_ALLOWLIST[resource.rel]}")
        resource.privacy_hits = []
    if resource.privacy_hits:
        resource.notes.append("疑似包含敏感信息，未纳入公开资源")


def should_include(resource: Resource) -> bool:
    if resource.name.startswith("~$"):
        resource.notes.append("Office 临时文件，未纳入公开资源")
        return False
    if resource.size == 0:
        resource.notes.append("空文件，未纳入公开资源")
        return False
    if resource.size > LARGE_LIMIT:
        resource.notes.append("超过 50 MiB，未纳入公开资源")
        return False
    if resource.size > HARD_LIMIT:
        resource.notes.append("超过 100 MiB，禁止提交")
        return False
    if resource.privacy_hits:
        return False
    return True


def copy_resources(resources: list[Resource]) -> None:
    first_by_hash: dict[str, Resource] = {}
    seen_dest_names: set[str] = set()
    for resource in resources:
        if not should_include(resource):
            resource.included = False
            continue
        duplicate_of = first_by_hash.get(resource.sha256)
        if duplicate_of:
            resource.included = True
            resource.dest_rel = duplicate_of.dest_rel
            resource.notes.append(f"重复文件，复用 {duplicate_of.rel}")
            continue
        resource.dest_rel = resource_dest(resource, seen_dest_names)
        dest = REPO_ROOT / "public" / resource.dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resource.source, dest)
        resource.included = True
        first_by_hash[resource.sha256] = resource


def resource_card(resource: Resource) -> str:
    title = html.escape(Path(resource.name).stem)
    url = html.escape(resource.public_url)
    kind = resource.ext.upper().lstrip(".") or "附件"
    label = html.escape(resource.module_label or resource.topic_label or "资料")
    card = [
        '<article class="resource-card">',
        '<div class="resource-card-head">',
        f"<h3>{title}</h3>",
        '<div class="resource-meta">',
        f"<span>{label}</span>",
        f"<span>{kind}</span>",
        f"<span>{resource.size_label}</span>",
        "</div>",
        "</div>",
        '<div class="resource-actions">',
        f'<a class="primary" href="{url}" target="_blank" rel="noopener">预览</a>',
        f'<a href="{url}" download>下载</a>',
        "</div>",
    ]
    if resource.ext == ".pdf":
        card.extend([
            f'<object class="pdf-preview" data="{url}" type="application/pdf">',
            f'<p>当前浏览器不支持内嵌 PDF 预览，请 <a href="{url}">下载文件</a> 查看。</p>',
            "</object>",
        ])
    card.append("</article>")
    return "\n".join(card)


def write_course_pages(resources: list[Resource]) -> tuple[dict[str, dict], dict[str, list[Resource]]]:
    courses: dict[str, dict] = {}
    course_resources: dict[str, list[Resource]] = {}
    for r in resources:
        if r.area == "course":
            courses.setdefault(r.course_slug, {"name": r.course_name, "slug": r.course_slug})
            course_resources.setdefault(r.course_slug, []).append(r)

    courses_dir = DOCS_ROOT / "resources" / "courses"
    courses_dir.mkdir(parents=True, exist_ok=True)

    for slug, info in sorted(courses.items(), key=lambda kv: kv[1]["name"]):
        course_dir = courses_dir / slug
        course_dir.mkdir(parents=True, exist_ok=True)
        items = [r for r in course_resources.get(slug, []) if r.included]
        by_module: dict[str, list[Resource]] = {}
        for item in items:
            by_module.setdefault(item.module_label, []).append(item)
        tags = [label for _, label in TYPE_ORDER if label in by_module]

        lines = [
            "---",
            f"title: {info['name']}",
            f"description: {info['name']}课程资料。",
            "---",
            "",
            "## 资料目录",
            "",
        ]
        if tags:
            lines.append('<div class="tag-list">')
            lines.extend(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags)
            lines.append("</div>")
        lines.append("")

        related_links = related_experience_links(info["name"])
        if related_links:
            lines.extend(["## 相关学习经验", ""])
            lines.extend(f"- [{title}]({BASE_PATH}{link})" for title, link in related_links)
            lines.append("")

        for _, label in TYPE_ORDER:
            module_items = sorted(by_module.get(label, []), key=lambda x: x.rel)
            if not module_items:
                continue
            lines.extend([f"## {label}", "", '<div class="resource-grid">'])
            lines.extend(resource_card(item) for item in module_items)
            lines.extend(["</div>", ""])

        (course_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")

    return courses, course_resources


_EXPERIENCE_INDEX: list[tuple[str, str, str]] = []
_LEARNING_BY_SEMESTER: dict[str, list[tuple[str, str]]] = {}
_OTHER_BY_CATEGORY: dict[str, list[tuple[str, str]]] = {}


def related_experience_links(course_name: str) -> list[tuple[str, str]]:
    aliases = [course_name, course_name.replace(" ", ""), course_name.replace("（", "(").replace("）", ")")]
    links = []
    for title, href, content in _EXPERIENCE_INDEX:
        if any(alias and alias in content for alias in aliases):
            links.append((title, href))
    return links[:8]


def write_experience_pages(resources: list[Resource]) -> tuple[list[Resource], list[Resource]]:
    learning = [r for r in resources if r.area == "learning" and r.ext in TEXT_EXTENSIONS and r.included]
    other = [r for r in resources if r.area == "other" and r.ext in TEXT_EXTENSIONS and r.included]
    _EXPERIENCE_INDEX.clear()
    _LEARNING_BY_SEMESTER.clear()
    _OTHER_BY_CATEGORY.clear()

    def write_note(resource: Resource, page_dir: Path, href: str, description: str) -> tuple[str, str, str]:
        slug = page_slug_for_resource(resource)
        page_dir = page_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        raw = read_text_file(resource.source)
        cleaned = clean_markdown(raw)
        title = Path(resource.name).stem
        content = "\n".join([
            "---",
            f"title: {title}",
            f"description: {description}",
            "---",
            "",
            cleaned,
        ])
        (page_dir / "index.md").write_text(content, encoding="utf-8")
        return title, f"{href}/{slug}/", cleaned

    for r in learning:
        semester_slug, semester_label = infer_learning_semester(r)
        base_dir = DOCS_ROOT / "experiences" / "learning" / "robotics" / semester_slug
        base_href = f"/experiences/learning/robotics/{semester_slug}"
        title, href, cleaned = write_note(r, base_dir, base_href, f"机器人工程{semester_label}学习经验。")
        _LEARNING_BY_SEMESTER.setdefault(semester_slug, []).append((title, href))
        _EXPERIENCE_INDEX.append((title, href, cleaned))
    for r in other:
        base_dir = DOCS_ROOT / "experiences" / "other" / r.topic_slug
        base_href = f"/experiences/other/{r.topic_slug}"
        title, href, cleaned = write_note(r, base_dir, base_href, f"{r.topic_label}经验资料。")
        _OTHER_BY_CATEGORY.setdefault(r.topic_slug, []).append((title, href))
        _EXPERIENCE_INDEX.append((title, href, cleaned))

    return learning, other


def link_card(title: str, href: str, tags: Iterable[str] = ()) -> str:
    tag_html = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in tags)
    tag_block = f'<div class="tag-list">{tag_html}</div>' if tag_html else ""
    return "\n".join([
        '<div class="cn-card">',
        f"<h3>{html.escape(title)}</h3>",
        tag_block,
        f'<a href="{href}">进入</a>',
        "</div>",
    ])


def write_index_pages(courses: dict[str, dict], course_resources: dict[str, list[Resource]], resources: list[Resource]) -> None:
    course_cards = []
    for slug, info in sorted(courses.items(), key=lambda kv: kv[1]["name"]):
        included = [r for r in course_resources.get(slug, []) if r.included]
        labels = []
        for _, label in TYPE_ORDER:
            if any(r.module_label == label for r in included):
                labels.append(label)
        tags = "\n".join(f'<span class="tag">{html.escape(label)}</span>' for label in labels)
        tag_block = f'<div class="tag-list">{tags}</div>' if tags else ""
        course_cards.append("\n".join([
            '<div class="cn-card">',
            f"<h3>{html.escape(info['name'])}</h3>",
            tag_block,
            f'<a href="./courses/{slug}/">进入课程页面</a>',
            "</div>",
        ]))

    resources_index = "\n".join([
        "---",
        "title: 学习资料",
        "description: 按课程组织的学习资料索引。",
        "---",
        "",
        '<div class="cn-grid">',
        *course_cards,
        "</div>",
    ])
    (DOCS_ROOT / "resources" / "index.md").write_text(resources_index, encoding="utf-8")

    learning_cards = "\n".join([
        link_card("自动化", "./automation/"),
        link_card("机器人工程", "./robotics/", [label for _, label in SEMESTER_ORDER]),
    ])
    learning_index = "\n".join([
        "---",
        "title: 学习经验",
        "description: 课程学习、备考、上课体验与避坑指南。",
        "---",
        "",
        '<div class="cn-grid">',
        learning_cards,
        "</div>",
    ])
    (DOCS_ROOT / "experiences" / "learning" / "index.md").write_text(learning_index, encoding="utf-8")

    automation_dir = DOCS_ROOT / "experiences" / "learning" / "automation"
    automation_dir.mkdir(parents=True, exist_ok=True)
    (automation_dir / "index.md").write_text("\n".join([
        "---",
        "title: 自动化",
        "description: 自动化专业学习经验。",
        "---",
        "",
    ]), encoding="utf-8")

    robotics_dir = DOCS_ROOT / "experiences" / "learning" / "robotics"
    robotics_dir.mkdir(parents=True, exist_ok=True)
    robotics_cards = "\n".join(link_card(label, f"./{slug}/") for slug, label in SEMESTER_ORDER)
    (robotics_dir / "index.md").write_text("\n".join([
        "---",
        "title: 机器人工程",
        "description: 机器人工程专业学习经验。",
        "---",
        "",
        '<div class="cn-grid">',
        robotics_cards,
        "</div>",
        "",
    ]), encoding="utf-8")

    for semester_slug, semester_label in SEMESTER_ORDER:
        semester_dir = robotics_dir / semester_slug
        semester_dir.mkdir(parents=True, exist_ok=True)
        rows = _LEARNING_BY_SEMESTER.get(semester_slug, [])
        cards = "\n".join(link_card(title, f"./{href.rstrip('/').split('/')[-1]}/") for title, href in rows)
        body = ['<div class="cn-grid">', cards, "</div>"] if cards else []
        (semester_dir / "index.md").write_text("\n".join([
            "---",
            f"title: {semester_label}",
            f"description: 机器人工程{semester_label}学习经验。",
            "---",
            "",
            *body,
            "",
        ]), encoding="utf-8")

    other_cards = "\n".join(link_card(label, f"./{slug}/") for slug, label in OTHER_CATEGORIES)
    other_index = "\n".join([
        "---",
        "title: 其他经验",
        "description: 六级、面试、升学、就业、考研、竞赛、工具与方法等非课程资料。",
        "---",
        "",
        '<div class="cn-grid">',
        other_cards,
        "</div>",
    ])
    (DOCS_ROOT / "experiences" / "other" / "index.md").write_text(other_index, encoding="utf-8")

    for slug, label in OTHER_CATEGORIES:
        category_dir = DOCS_ROOT / "experiences" / "other" / slug
        category_dir.mkdir(parents=True, exist_ok=True)
        rows = _OTHER_BY_CATEGORY.get(slug, [])
        if rows:
            cards = "\n".join(link_card(title, f"./{href.rstrip('/').split('/')[-1]}/") for title, href in rows)
            body = ['<div class="cn-grid">', cards, "</div>"]
        else:
            body = []
        (category_dir / "index.md").write_text("\n".join([
            "---",
            f"title: {label}",
            f"description: {label}相关经验资料。",
            "---",
            "",
            *body,
            "",
        ]), encoding="utf-8")

    pending = [r for r in resources if r.area == "pending"]
    if pending:
        pending_dir = DOCS_ROOT / "resources" / "pending"
        pending_dir.mkdir(parents=True, exist_ok=True)
        cards = "\n".join(resource_card(r) for r in pending if r.included)
        pending_page = "\n".join([
            "---",
            "title: 待分类资料",
            "description: 尚未能自动判断课程或类型的资料。",
            "---",
            "",
            "以下资料暂未能自动判断课程或类型，后续可人工移动到对应课程页面。",
            "",
            '<div class="resource-grid">',
            cards or "<p>暂无可公开待分类资料。</p>",
            "</div>",
        ])
        (pending_dir / "index.md").write_text(pending_page, encoding="utf-8")


def write_sidebar(courses: dict[str, dict], resources: list[Resource]) -> None:
    course_items = [
        {"label": info["name"], "slug": f"resources/courses/{slug}"}
        for slug, info in sorted(courses.items(), key=lambda kv: kv[1]["name"])
    ]
    pending_exists = any(r.area == "pending" and r.included for r in resources)
    if pending_exists:
        course_items.append({"label": "待分类资料", "slug": "resources/pending"})
    sidebar = [
        {"label": "首页", "slug": "index"},
        {"label": "学习资料", "items": [{"label": "课程索引", "slug": "resources"}, *course_items]},
        {"label": "学习经验", "items": [
            {"label": "自动化", "slug": "experiences/learning/automation"},
            {"label": "机器人工程", "items": [
                {"label": label, "slug": f"experiences/learning/robotics/{slug}"}
                for slug, label in SEMESTER_ORDER
            ]},
        ]},
        {"label": "其他经验", "items": [
            {"label": label, "slug": f"experiences/other/{slug}"}
            for slug, label in OTHER_CATEGORIES
        ]},
        {"label": "资料贡献", "slug": "contribute"},
        {"label": "关于项目", "slug": "about"},
    ]
    content = "export const generatedSidebar = " + json.dumps(sidebar, ensure_ascii=False, indent=2) + ";\n"
    (REPO_ROOT / "src" / "generated" / "sidebar.mjs").write_text(content, encoding="utf-8")


def write_reports(resources: list[Resource]) -> dict:
    internal_dir = DOCS_ROOT / "internal"
    internal_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        "| 原始相对路径 | 文件名 | 推测课程名 | 推测模块 | 文件类型 | 文件大小 | 是否被纳入网站 | 备注 |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for r in sorted(resources, key=lambda x: x.rel):
        course = r.course_name or r.topic_label or "待分类"
        module = r.module_label or r.topic_label or "待分类"
        note = "；".join(r.notes) if r.notes else ""
        rows.append(
            f"| {md_escape(r.rel)} | {md_escape(r.name)} | {md_escape(course)} | {md_escape(module)} | {md_escape(r.ext or '无扩展名')} | {r.size_label} | {'是' if r.included else '否'} | {md_escape(note)} |"
        )
    inventory = "\n".join([
        "---",
        "title: 资料清单",
        "description: 内部资料分类清单，不显示在公开导航中。",
        "sidebar:",
        "  hidden: true",
        "---",
        "",
        "# 资料清单",
        "",
        "本页面用于维护者核对资料分类结果，未加入公开导航。",
        "",
        *rows,
        "",
    ])
    (internal_dir / "resource-inventory.md").write_text(inventory, encoding="utf-8")

    large = [r for r in resources if r.size > LARGE_LIMIT]
    large_lines = ["# Large Files Report", ""]
    if large:
        large_lines.extend(["| 文件 | 大小 | 建议处理方式 |", "| --- | ---: | --- |"])
        for r in large:
            advice = "压缩 PDF、拆分文件、放入 GitHub Release，或外部网盘托管后在网站中提供链接。"
            large_lines.append(f"| `{md_escape(r.rel)}` | {r.size_label} | {advice} |")
    else:
        large_lines.append("未发现超过 50 MiB 的文件。")
    (REPORTS_ROOT / "large-files-report.md").write_text("\n".join(large_lines) + "\n", encoding="utf-8")

    sensitive = [r for r in resources if r.privacy_hits]
    sensitive_lines = ["# Sensitive Review Needed", ""]
    if sensitive:
        sensitive_lines.extend(["| 文件 | 命中类型 | 处理状态 |", "| --- | --- | --- |"])
        for r in sensitive:
            sensitive_lines.append(f"| `{md_escape(r.rel)}` | {', '.join(r.privacy_hits)} | 未纳入公开资源，等待人工确认 |")
    else:
        sensitive_lines.append("未发现自动规则命中的疑似敏感文件。图片内容未做 OCR，请人工抽查。")
    (REPORTS_ROOT / "sensitive-review-needed.md").write_text("\n".join(sensitive_lines) + "\n", encoding="utf-8")

    stats = {
        "course_count": len({r.course_slug for r in resources if r.area == "course"}),
        "course_resource_files": len([r for r in resources if r.area == "course" and r.included]),
        "learning_experience_files": len([r for r in resources if r.area == "learning" and r.included]),
        "other_experience_files": len([r for r in resources if r.area == "other" and r.included]),
        "pending_files": len([r for r in resources if r.area == "pending"]),
        "large_skipped_files": len([r for r in resources if r.size > LARGE_LIMIT]),
        "sensitive_review_files": len(sensitive),
        "total_files_scanned": len(resources),
    }
    (REPORTS_ROOT / "generation-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    if not SOURCE_ROOT.exists():
        print(f"Source directory not found: {SOURCE_ROOT}", file=sys.stderr)
        return 1

    ensure_clean_generated_dirs()
    files = sorted(p for p in SOURCE_ROOT.rglob("*") if p.is_file())
    resources: list[Resource] = []
    for path in files:
        sha = sha256_file(path)
        resource = classify(path, sha)
        privacy_scan(resource)
        resources.append(resource)

    copy_resources(resources)
    learning, other = write_experience_pages(resources)
    courses, course_resources = write_course_pages(resources)
    write_index_pages(courses, course_resources, resources)
    write_sidebar(courses, resources)
    stats = write_reports(resources)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"Generated from: {SOURCE_ROOT}")
    print(f"Learning pages: {len(learning)}; other pages: {len(other)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
