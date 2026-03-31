from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


def u(text: str) -> str:
    return text.encode("ascii").decode("unicode_escape")


def build_pdf(output_path: Path) -> None:
    pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="KTitle",
            parent=styles["Title"],
            fontName="Malgun",
            fontSize=18,
            leading=24,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KHeading",
            parent=styles["Heading2"],
            fontName="Malgun",
            fontSize=12,
            leading=18,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KBody",
            parent=styles["BodyText"],
            fontName="Malgun",
            fontSize=10.5,
            leading=16,
            spaceAfter=4,
        )
    )

    sections = [
        (
            u("1. TMAP App Key \\ubc1c\\uae09"),
            [
                u("SK open API \\uc0ac\\uc774\\ud2b8(https://openapi.sk.com/)\\uc5d0 \\uc811\\uc18d\\ud574 \\ud68c\\uc6d0\\uac00\\uc785 \\ub610\\ub294 \\ub85c\\uadf8\\uc778\\ud569\\ub2c8\\ub2e4."),
                u("TMAP \\uad00\\ub828 \\uc0c1\\ud488\\uc73c\\ub85c \\uc774\\ub3d9\\ud569\\ub2c8\\ub2e4."),
                u("\\ubcf4\\ud589\\uc790 \\uacbd\\ub85c \\uc548\\ub0b4, Geocoding \\ub610\\ub294 Full Text Geocoding \\uc0c1\\ud488\\uc758 \\uc0ac\\uc6a9 \\uc2e0\\uccad \\uc5ec\\ubd80\\ub97c \\ud655\\uc778\\ud569\\ub2c8\\ub2e4."),
                u("\\uc571 \\uc0ac\\uc6a9\\ud558\\uae30 \\ub610\\ub294 \\uc720\\uc0ac\\ud55c \\uba54\\ub274\\uc5d0\\uc11c \\uc571\\uc744 \\uc0dd\\uc131\\ud569\\ub2c8\\ub2e4."),
                u("\\ubc1c\\uae09\\ub41c App Key\\ub97c \\ubcf5\\uc0ac\\ud569\\ub2c8\\ub2e4."),
            ],
        ),
        (
            u("2. \\ub85c\\uceec \\uc571\\uc5d0 Key \\uc800\\uc7a5"),
            [
                u("\\uc571 \\uc2e4\\ud589 \\ud6c4 \\uc67c\\ucabd \\uc0ac\\uc774\\ub4dc\\ubc14\\uc758 TMAP API \\uc124\\uc815 \\uc601\\uc5ed\\uc744 \\uc5fd\\ub2c8\\ub2e4."),
                u("TMAP App Key \\ubcc0\\uacbd \\uc785\\ub825\\uce78\\uc5d0 \\ubc1c\\uae09\\ubc1b\\uc740 \\ud0a4\\ub97c \\ubd99\\uc5ec\\ub123\\uc2b5\\ub2c8\\ub2e4."),
                u("TMAP \\ud0a4 \\uc800\\uc7a5 \\ubc84\\ud2bc\\uc744 \\ub204\\ub985\\ub2c8\\ub2e4."),
                u("\\ub2e8\\uac74 \\uc870\\ud68c\\ub85c \\uc8fc\\uc18c 1\\uac74\\uc744 \\ud14c\\uc2a4\\ud2b8\\ud569\\ub2c8\\ub2e4."),
            ],
        ),
        (
            u("3. \\ubc30\\ud3ec\\ub41c Streamlit \\uc571\\uc5d0 Key \\uc800\\uc7a5"),
            [
                u("Streamlit Community Cloud\\uc5d0\\uc11c \\ud574\\ub2f9 \\uc571\\uc744 \\uc5fd\\ub2c8\\ub2e4."),
                u("Manage app \\ub610\\ub294 Settings\\ub85c \\uc774\\ub3d9\\ud569\\ub2c8\\ub2e4."),
                u("Secrets \\ud0ed\\uc744 \\uc5fd\\ub2c8\\ub2e4."),
                u("TMAP_APP_KEY = \\\"\\ubc1c\\uae09\\ubc1b\\uc740\\ud0a4\\\" \\ud615\\ud0dc\\ub85c \\uc800\\uc7a5\\ud569\\ub2c8\\ub2e4."),
                u("\\uc800\\uc7a5 \\ud6c4 \\uc571\\uc744 \\ub2e4\\uc2dc \\ud655\\uc778\\ud569\\ub2c8\\ub2e4."),
            ],
        ),
        (
            u("4. \\uc815\\uc0c1 \\ub3d9\\uc791 \\ud655\\uc778"),
            [
                u("\\ub2e8\\uac74 \\uc870\\ud68c\\uc5d0\\uc11c \\ucd9c\\ubc1c\\uc9c0\\uc640 \\ub3c4\\ucc29\\uc9c0\\ub97c \\uc785\\ub825\\ud574 \\uacb0\\uacfc\\ub97c \\ud655\\uc778\\ud569\\ub2c8\\ub2e4."),
                u("\\ub610\\ub294 \\uc0d8\\ud50c \\uc5d1\\uc140 \\ud30c\\uc77c\\uc744 \\uc5c5\\ub85c\\ub4dc\\ud574 \\uacb0\\uacfc \\ud30c\\uc77c \\ub2e4\\uc6b4\\ub85c\\ub4dc\\ub97c \\ud655\\uc778\\ud569\\ub2c8\\ub2e4."),
                u("\\uc815\\uc0c1\\uc774\\ub77c\\uba74 \\ub3c4\\ubcf4 \\uac70\\ub9ac\\uc640 \\uc608\\uc0c1 \\uc2dc\\uac04\\uc774 \\ud45c\\uc2dc\\ub418\\uace0, \\ud558\\ub2e8 \\uc0ac\\uc6a9\\ub7c9 \\uce74\\ub4dc \\uc22b\\uc790\\uac00 \\uc99d\\uac00\\ud569\\ub2c8\\ub2e4."),
            ],
        ),
        (
            u("5. \\uc8fc\\uc758\\uc0ac\\ud56d"),
            [
                u("App Key\\ub97c GitHub\\uc5d0 \\uc62c\\ub9ac\\uba74 \\uc548 \\ub429\\ub2c8\\ub2e4."),
                u("config.json\\uc5d0 \\ud0a4\\ub97c \\ub123\\uc5c8\\ub2e4\\uba74 \\uc800\\uc7a5\\uc18c\\uc5d0 \\ucee4\\ubc0b\\ud558\\uc9c0 \\uc54a\\uc2b5\\ub2c8\\ub2e4."),
                u("\\ubc30\\ud3ec \\ud658\\uacbd\\uc5d0\\uc11c\\ub294 Streamlit Secrets \\uc0ac\\uc6a9\\uc744 \\uad8c\\uc7a5\\ud569\\ub2c8\\ub2e4."),
                u("\\ud0a4 \\uc624\\ub958\\ub098 \\uad8c\\ud55c \\ubb38\\uc81c \\uc2dc 401 \\ub610\\ub294 403, \\ud55c\\ub3c4 \\ucd08\\uacfc \\uac00\\ub2a5 \\uc2dc 429 \\uc548\\ub0b4\\uac00 \\ud45c\\uc2dc\\ub420 \\uc218 \\uc788\\uc2b5\\ub2c8\\ub2e4."),
            ],
        ),
    ]

    story = [
        Paragraph(u("TMAP API Key \\ubc1c\\uae09 \\ubc0f \\uc800\\uc7a5 \\uc548\\ub0b4\\uc11c"), styles["KTitle"]),
        Paragraph(
            u("\\ub300\\uc0c1: \\uc571 \\uc6b4\\uc601 \\ub2f4\\ub2f9\\uc790 / \\ubaa9\\uc801: TMAP App Key\\ub97c \\ubc1c\\uae09\\ubc1b\\uc544 \\uc571 \\ub610\\ub294 \\ubc30\\ud3ec \\ud658\\uacbd\\uc5d0 \\uc800\\uc7a5\\ud558\\uace0 \\uc815\\uc0c1 \\ub3d9\\uc791\\uc744 \\ud655\\uc778\\ud569\\ub2c8\\ub2e4."),
            styles["KBody"],
        ),
    ]

    for heading, bullets in sections:
        story.append(Paragraph(heading, styles["KHeading"]))
        story.append(
            ListFlowable(
                [ListItem(Paragraph(item, styles["KBody"])) for item in bullets],
                bulletType="bullet",
                leftIndent=16,
            )
        )
        story.append(Spacer(1, 4))

    story.append(Paragraph(u("\\ucc38\\uace0 \\ub9c1\\ud06c"), styles["KHeading"]))
    for link in [
        "SK open API: https://openapi.sk.com/",
        "TMAP API: https://tmapapi.tmapmobility.com/",
        "Streamlit Secrets: https://docs.streamlit.io/develop/concepts/connections/secrets-management",
    ]:
        story.append(Paragraph(link, styles["KBody"]))

    SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    ).build(story)


if __name__ == "__main__":
    build_pdf(Path("TMAP_API_Key_Guide.pdf"))
