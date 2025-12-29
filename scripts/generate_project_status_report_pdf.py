from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (  # type: ignore
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _md_to_story(md_text: str):
    styles = getSampleStyleSheet()
    title = styles["Title"]
    h2 = styles["Heading2"]
    h3 = styles["Heading3"]
    body = styles["BodyText"]

    story = []
    bullet_items: list[ListItem] = []

    def flush_bullets():
        nonlocal bullet_items
        if bullet_items:
            story.append(
                ListFlowable(
                    bullet_items,
                    bulletType="bullet",
                    leftIndent=14,
                )
            )
            story.append(Spacer(1, 6))
            bullet_items = []

    for raw in md_text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_bullets()
            continue

        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(line[2:].strip(), title))
            story.append(Spacer(1, 10))
            continue
        if line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(line[3:].strip(), h2))
            story.append(Spacer(1, 6))
            continue
        if line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(line[4:].strip(), h3))
            story.append(Spacer(1, 4))
            continue

        if line.startswith("- "):
            text = line[2:].strip()
            bullet_items.append(ListItem(Paragraph(text, body)))
            continue

        # Regular paragraph
        flush_bullets()
        story.append(Paragraph(line.strip(), body))
        story.append(Spacer(1, 4))

    flush_bullets()
    return story


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    md_path = repo_root / "docs" / "project_status_report.md"
    pdf_path = repo_root / "docs" / "project_status_report.pdf"

    if not md_path.exists():
        raise SystemExit(f"Missing Markdown source: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    story = _md_to_story(md_text)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="LivingBetterCC — Reporte de estado",
        author="LivingBetterCC",
    )
    doc.build(story)

    print(f"Wrote: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
