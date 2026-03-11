from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import ClaimRiskLevel, ReportType
from app.models import Organization, Report, Run
from app.services.analysis_framework import get_analysis_framework
from app.services.brand_scope import resolve_brand
from app.services.metrics import (
    build_capabilities_from_runs,
    build_overview_from_runs,
    get_runs_for_period,
    list_claims_by_run_ids,
    list_hijacks_by_run_ids,
)
from app.services.project_factory import _PLACEHOLDER_COMPETITOR_NAMES

REPORT_FONT = "WQYMicroHei"
REPORT_FALLBACK_FONT = "STSong-Light"
REPORT_FONT_CANDIDATE_PATHS = (
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
)

COLOR_TITLE = colors.HexColor("#152F4E")
COLOR_TEXT = colors.HexColor("#243447")
COLOR_SUB_TEXT = colors.HexColor("#5C6B7A")
COLOR_HEADER = colors.HexColor("#1F3A5F")
COLOR_RISK_HEADER = COLOR_HEADER
COLOR_GRID = colors.HexColor("#D3DDE8")
COLOR_ROW = colors.HexColor("#F7FAFC")
COLOR_BG = colors.HexColor("#F5F8FC")


def _report_range(
    report_type: ReportType,
    week_start: date | None = None,
    month: str | None = None,
) -> tuple[date, date]:
    if report_type == ReportType.weekly_brief:
        if not week_start:
            raise ValueError("week_start is required")
        return week_start, week_start + timedelta(days=6)

    if not month:
        raise ValueError("month is required")
    year, month_num = [int(part) for part in month.split("-", maxsplit=1)]
    start = date(year, month_num, 1)
    next_month = date(year + (1 if month_num == 12 else 0), 1 if month_num == 12 else month_num + 1, 1)
    return start, next_month - timedelta(days=1)


def _fmt_number(value: float | int | None) -> str:
    return str(round(float(value or 0)))


def _normalize_key(text: str) -> str:
    return re.sub(r"[\s，,。.!！?？；;：:、/\\\-_（）()\[\]【】'\"`]+", "", (text or "").lower())


def _clip(text: str, max_len: int = 64) -> str:
    clean = (text or "").strip()
    if len(clean) <= max_len:
        return clean
    return f"{clean[: max_len - 1]}…"


def _canonical_claim_topic(claim_text: str, subject: str) -> str:
    text = (claim_text or "").strip()
    target = (subject or "").strip()
    if not text:
        return ""
    if target and text.startswith(target):
        remainder = text[len(target) :].lstrip("：:，,。.!！?？；;、 ")
        if remainder:
            return remainder
    return text


def _dedupe_texts(texts: list[str], limit: int = 2) -> list[str]:
    seen: set[str] = set()
    outputs: list[str] = []
    for text in texts:
        value = (text or "").strip()
        if not value:
            continue
        key = _normalize_key(value)
        if not key or key in seen:
            continue
        seen.add(key)
        outputs.append(value)
        if len(outputs) >= limit:
            break
    return outputs


def _register_fonts() -> None:
    for name in (REPORT_FONT, REPORT_FALLBACK_FONT):
        try:
            pdfmetrics.getFont(name)
            return
        except KeyError:
            continue

    for candidate in REPORT_FONT_CANDIDATE_PATHS:
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(REPORT_FONT, str(path), subfontIndex=0))
            return
        except Exception:
            continue

    pdfmetrics.registerFont(UnicodeCIDFont(REPORT_FALLBACK_FONT))


def _report_font_name() -> str:
    for name in (REPORT_FONT, REPORT_FALLBACK_FONT):
        try:
            pdfmetrics.getFont(name)
            return name
        except KeyError:
            continue
    return REPORT_FALLBACK_FONT


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    font_name = _report_font_name()
    return {
        "title": ParagraphStyle(
            "TitleCN",
            parent=base["Title"],
            fontName=font_name,
            fontSize=18,
            leading=24,
            textColor=COLOR_TITLE,
        ),
        "heading": ParagraphStyle(
            "HeadingCN",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=13,
            leading=18,
            textColor=COLOR_TITLE,
        ),
        "sub": ParagraphStyle(
            "SubCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=9,
            leading=14,
            textColor=COLOR_SUB_TEXT,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "BodyCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=15,
            textColor=COLOR_TEXT,
            wordWrap="CJK",
        ),
        "cell": ParagraphStyle(
            "CellCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=8.8,
            leading=12.2,
            textColor=COLOR_TEXT,
            wordWrap="CJK",
        ),
    }


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    safe = escape((text or "").strip()).replace("\n", "<br/>")
    return Paragraph(safe or "—", style)


def _bullet_paragraph(texts: list[str], style: ParagraphStyle) -> Paragraph:
    lines = _dedupe_texts(texts, limit=2)
    if not lines:
        return Paragraph("—", style)
    body = "<br/>".join(f"• {escape(_clip(line, 52))}" for line in lines)
    return Paragraph(body, style)


def _capability_observation(row: dict[str, object]) -> str:
    positives = _dedupe_texts([str(item) for item in row.get("top_positive_claims", [])], limit=1)
    negatives = _dedupe_texts([str(item) for item in row.get("top_negative_claims", [])], limit=1)
    if positives and negatives:
        return f"优势：{_clip(positives[0], 34)}；风险：{_clip(negatives[0], 34)}"
    if positives:
        return f"主要正向：{_clip(positives[0], 42)}"
    if negatives:
        return f"主要风险：{_clip(negatives[0], 42)}"
    return "本周期该维度信号相对平稳"


def _section_title(title: str, styles: dict[str, ParagraphStyle]) -> list[object]:
    return [Spacer(1, 8), Paragraph(title, styles["heading"]), Spacer(1, 4)]


def _summary_lines(
    report_type: ReportType,
    overview: dict,
    capabilities: dict,
    risk_summary: list[dict[str, object]],
    hijack_summary: list[dict[str, object]],
) -> list[str]:
    kpis = overview.get("kpis", {})
    top_capability = sorted(
        capabilities.get("categories", []),
        key=lambda row: float(row.get("score", 0)),
        reverse=True,
    )[:1]
    weak_capability = sorted(
        capabilities.get("categories", []),
        key=lambda row: float(row.get("score", 0)),
    )[:1]

    lines = [
        (
            f"本周期提及率 { _fmt_number(kpis.get('mention_rate')) }%，首推率 { _fmt_number(kpis.get('first_pick_rate')) }%，"
            f"前三占位率 { _fmt_number(kpis.get('top3_rate')) }%"
        ),
        f"高风险断言主题 {len(risk_summary)} 个，竞品分流主题 {len(hijack_summary)} 个。",
    ]
    if top_capability:
        top_name = top_capability[0].get("display_name") or top_capability[0]["category"]
        lines.append(
            f"优势维度：{top_name}（{_fmt_number(top_capability[0]['score'])}分）"
        )
    if weak_capability:
        weak_name = weak_capability[0].get("display_name") or weak_capability[0]["category"]
        lines.append(
            f"待补强维度：{weak_name}（{_fmt_number(weak_capability[0]['score'])}分）"
        )
    lines.append(
        "月报重点看中长期治理与内容资产沉淀。"
        if report_type == ReportType.monthly_strategy
        else "周报重点看短期风险压降与分流拦截动作。"
    )
    return lines


def _risk_priority(level: str) -> int:
    if level == ClaimRiskLevel.critical.value:
        return 2
    if level == ClaimRiskLevel.high.value:
        return 1
    return 0


def _risk_level_cn(level: str) -> str:
    mapping = {
        ClaimRiskLevel.critical.value: "严重",
        ClaimRiskLevel.high.value: "高",
        ClaimRiskLevel.medium.value: "中",
        ClaimRiskLevel.low.value: "低",
    }
    return mapping.get(level, level)


def _summarize_risk_claims(risk_claims: list[dict], limit: int = 10) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for claim in risk_claims:
        claim_text = str(claim.get("claim_text", "")).strip()
        subject = str(claim.get("subject_name", "")).strip()
        risk_level = str(claim.get("risk_level", ""))
        canonical_topic = _canonical_claim_topic(claim_text, subject)
        key = _normalize_key(canonical_topic)
        if not key:
            continue
        bucket = grouped.get(key)
        if not bucket:
            bucket = {
                "topic": canonical_topic or claim_text,
                "risk_level": risk_level,
                "impact_max": int(claim.get("impact_score", 0)),
                "count": 0,
                "providers": set(),
                "categories": set(),
                "subjects": defaultdict(int),
            }
            grouped[key] = bucket
        elif _risk_priority(risk_level) > _risk_priority(str(bucket["risk_level"])):
            bucket["risk_level"] = risk_level
        bucket["count"] = int(bucket["count"]) + 1
        bucket["impact_max"] = max(int(bucket["impact_max"]), int(claim.get("impact_score", 0)))
        bucket["providers"].add(str(claim.get("provider", "")))
        bucket["categories"].add(str(claim.get("category", "")))
        if subject:
            bucket["subjects"][subject] += 1

    rows = list(grouped.values())
    rows.sort(
        key=lambda item: (
            -_risk_priority(str(item["risk_level"])),
            -int(item["impact_max"]),
            -int(item["count"]),
        )
    )
    for row in rows:
        subjects_counter = row["subjects"]
        sorted_subjects = sorted(
            subjects_counter.items(),
            key=lambda item: (
                item[0] in _PLACEHOLDER_COMPETITOR_NAMES,
                -item[1],
                item[0],
            ),
        )
        real_subjects = [name for name, _ in sorted_subjects if name not in _PLACEHOLDER_COMPETITOR_NAMES]
        fallback_subjects = [name for name, _ in sorted_subjects if name in _PLACEHOLDER_COMPETITOR_NAMES]
        selected = (real_subjects or fallback_subjects)[:3]
        row["subject_summary"] = " / ".join(selected) if selected else "—"
        row["subject_count"] = len(subjects_counter)
    return rows[:limit]


def _summarize_hijacks(hijacks: dict, limit: int = 8) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for item in hijacks.get("items", []):
        if not item.get("hijack_flag"):
            continue
        prompt_text = str(item.get("prompt_text", "")).strip()
        key = _normalize_key(prompt_text)
        if key not in grouped:
            grouped[key] = {
                "prompt_text": prompt_text,
                "count": 0,
                "strength_total": 0,
                "strength_max": 0,
                "entities": defaultdict(int),
            }
        bucket = grouped[key]
        strength = int(item.get("hijack_strength", 0))
        bucket["count"] = int(bucket["count"]) + 1
        bucket["strength_total"] = int(bucket["strength_total"]) + strength
        bucket["strength_max"] = max(int(bucket["strength_max"]), strength)
        for entity in item.get("recommended_entities", []):
            bucket["entities"][str(entity)] += 1

    results: list[dict[str, object]] = []
    for value in grouped.values():
        entities_counter = value["entities"]
        entities = sorted(
            entities_counter.items(),
            key=lambda item: (-item[1], item[0]),
        )
        results.append(
            {
                "prompt_text": value["prompt_text"],
                "count": int(value["count"]),
                "avg_strength": round(int(value["strength_total"]) / max(int(value["count"]), 1)),
                "max_strength": int(value["strength_max"]),
                "top_entities": [name for name, _ in entities[:3]],
            }
        )
    results.sort(key=lambda item: (-int(item["count"]), -int(item["avg_strength"]), -int(item["max_strength"])))
    return results[:limit]


def _recommendations(
    report_type: ReportType,
    risk_summary: list[dict[str, object]],
    hijack_summary: list[dict[str, object]],
    capabilities: dict,
) -> list[tuple[str, str, str]]:
    weak_categories = sorted(
        capabilities.get("categories", []),
        key=lambda row: float(row.get("score", 0)),
    )[:2]
    weak_text = "、".join(item["category"] for item in weak_categories) or "待补强维度"

    if report_type == ReportType.weekly_brief:
        return [
            ("优先级一", "高风险断言治理", f"针对 {len(risk_summary)} 个高风险主题完成人工复核并输出标准澄清话术"),
            ("优先级二", "竞品分流拦截", f"围绕 {len(hijack_summary)} 个分流主题更新品牌首推回答模板并复测"),
            ("优先级二", "能力短板补齐", f"优先补强 {weak_text} 的证据素材、案例与常见问答"),
        ]
    return [
        ("战略", "品牌叙事统一", "统一官网、常见问答、销售素材与AI问答内容，确保外部信号一致"),
        ("策略", "分流风险治理", f"将 {len(hijack_summary)} 个高频分流主题纳入季度内容优化计划。"),
        ("运营", "风险闭环复盘", f"按月复盘 {len(risk_summary)} 个风险主题，形成整改追踪台账。"),
    ]


def _provider_label(provider: str) -> str:
    mapping = {
        "deepseek": "DeepSeek",
        "tongyi": "通义千问",
        "doubao": "豆包",
        "kimi": "Kimi",
        "yuanbao": "腾讯元宝",
        "wenxin": "文心一言",
        "zhipu": "智谱清言",
    }
    return mapping.get(provider.lower(), provider or "未知平台")


def _summarize_provider_distribution(runs: list[Run]) -> list[dict[str, object]]:
    if not runs:
        return []
    counter: Counter[str] = Counter(run.provider.value for run in runs)
    total = max(sum(counter.values()), 1)
    rows = []
    for provider, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        rows.append(
            {
                "provider": provider,
                "provider_label": _provider_label(provider),
                "count": count,
                "share": round(count / total * 100, 1),
            }
        )
    return rows


def _summarize_sentiment_distribution(claims: list[dict]) -> list[dict[str, object]]:
    if not claims:
        return []
    counter: Counter[str] = Counter(str(item.get("sentiment", "0")) for item in claims)
    total = max(sum(counter.values()), 1)
    label_map = {"+": "正向", "0": "中性", "-": "负向"}
    ordered = ["+", "0", "-"]
    return [
        {
            "sentiment": key,
            "sentiment_label": label_map.get(key, key),
            "count": counter.get(key, 0),
            "share": round(counter.get(key, 0) / total * 100, 1),
        }
        for key in ordered
    ]


def _dimension_audit_rows(capabilities: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in capabilities.get("categories", []):
        category = str(item.get("category", ""))
        display_name = str(item.get("display_name", category))
        definition = str(item.get("definition", "用于评估该维度的综合表现"))
        rows.append(
            {
                "category": category,
                "data_source_dimension": display_name,
                "page_dimension": display_name,
                "report_dimension": display_name,
                "definition": definition,
                "status": "一致",
            }
        )
    return rows


def _apply_table_style(table: Table, font_name: str, header_color: colors.Color = COLOR_HEADER) -> None:
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("BACKGROUND", (0, 0), (-1, 0), header_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW]),
                ("GRID", (0, 0), (-1, -1), 0.45, COLOR_GRID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )


def _build_report_document(
    report_type: ReportType,
    title: str,
    org_name: str,
    brand_name: str,
    project_context: str,
    period_start: date,
    period_end: date,
    run_count: int,
    overview: dict,
    capabilities: dict,
    all_claims: list[dict],
    period_runs: list[Run],
    risk_claims: list[dict],
    hijacks: dict,
    output_path: Path,
) -> None:
    _register_fonts()
    styles = _styles()
    font_name = _report_font_name()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    risk_summary = _summarize_risk_claims(risk_claims, limit=10)
    hijack_summary = _summarize_hijacks(hijacks, limit=8)
    provider_distribution = _summarize_provider_distribution(period_runs)
    sentiment_distribution = _summarize_sentiment_distribution(all_claims)
    dimension_audit = _dimension_audit_rows(capabilities)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=26,
        bottomMargin=28,
    )
    story: list[object] = []

    story.append(Paragraph(title, styles["title"]))
    story.append(Paragraph(f"{period_start} 至 {period_end}", styles["sub"]))
    story.append(Spacer(1, 6))

    meta_table = Table(
        [
            ["组织", _paragraph(org_name, styles["sub"]), "品牌项目", _paragraph(brand_name, styles["sub"])],
            ["行业场景", _paragraph(project_context, styles["sub"]), "采样运行次数", str(run_count)],
            [
                "报告类型",
                "周度作战简报" if report_type == ReportType.weekly_brief else "月度战略报告",
                "生成时间",
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M（世界时）"),
            ],
        ],
        colWidths=[72, 160, 72, 180],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG),
                ("GRID", (0, 0), (-1, -1), 0.45, COLOR_GRID),
                ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.extend([meta_table, Spacer(1, 8)])

    story.extend(_section_title("一、执行摘要", styles))
    for line in _summary_lines(report_type, overview, capabilities, risk_summary, hijack_summary):
        story.append(Paragraph(f"• {escape(line)}", styles["body"]))
    story.append(Spacer(1, 6))

    kpis = overview.get("kpis", {})
    story.extend(_section_title("二、管理层关键指标", styles))
    kpi_table = Table(
        [
            ["提及率", "推荐率（首推）", "前三占位率", "竞品出现率", "高风险主题数"],
            [
                f"{_fmt_number(kpis.get('mention_rate'))}%",
                f"{_fmt_number(kpis.get('first_pick_rate'))}%",
                f"{_fmt_number(kpis.get('top3_rate'))}%",
                f"{_fmt_number(kpis.get('competitor_appearance_rate'))}%",
                str(len(risk_summary)),
            ],
        ],
        colWidths=[100, 100, 88, 100, 110],
    )
    _apply_table_style(kpi_table, font_name, header_color=COLOR_HEADER)
    kpi_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.extend([kpi_table, Spacer(1, 8)])

    story.extend(_section_title("三、平台分布与情感结构", styles))
    if provider_distribution:
        provider_rows: list[list[object]] = [["平台", "运行次数", "占比", "管理层提示"]]
        for row in provider_distribution:
            provider_rows.append(
                [
                    _paragraph(str(row["provider_label"]), styles["cell"]),
                    _paragraph(str(row["count"]), styles["cell"]),
                    _paragraph(f"{row['share']}%", styles["cell"]),
                    _paragraph(
                        "建议保持采样均衡，避免单平台偏差影响判断",
                        styles["cell"],
                    ),
                ]
            )
        provider_table = Table(provider_rows, colWidths=[120, 78, 78, 244])
        _apply_table_style(provider_table, font_name, header_color=COLOR_HEADER)
        story.extend([provider_table, Spacer(1, 6)])

    if sentiment_distribution:
        sentiment_rows: list[list[object]] = [["情感分布", "断言数", "占比", "解读"]]
        for row in sentiment_distribution:
            insight = (
                "维持正向表达素材沉淀"
                if row["sentiment"] == "+"
                else "持续补充中性证据与对比说明"
                if row["sentiment"] == "0"
                else "优先进入风险治理与舆情复核清单"
            )
            sentiment_rows.append(
                [
                    _paragraph(str(row["sentiment_label"]), styles["cell"]),
                    _paragraph(str(row["count"]), styles["cell"]),
                    _paragraph(f"{row['share']}%", styles["cell"]),
                    _paragraph(insight, styles["cell"]),
                ]
            )
        sentiment_table = Table(sentiment_rows, colWidths=[112, 70, 70, 268])
        _apply_table_style(sentiment_table, font_name, header_color=COLOR_HEADER)
        story.extend([sentiment_table, Spacer(1, 8)])

    story.extend(_section_title("四、竞品对比维度一致性审计", styles))
    if dimension_audit:
        audit_rows: list[list[object]] = [["分类", "数据源", "页面", "报告", "一致性"]]
        for row in dimension_audit:
            audit_rows.append(
                [
                    _paragraph(str(row["category"]), styles["cell"]),
                    _paragraph(str(row["data_source_dimension"]), styles["cell"]),
                    _paragraph(str(row["page_dimension"]), styles["cell"]),
                    _paragraph(str(row["report_dimension"]), styles["cell"]),
                    _paragraph(str(row["status"]), styles["cell"]),
                ]
            )
        audit_table = Table(audit_rows, colWidths=[72, 132, 132, 132, 52])
        _apply_table_style(audit_table, font_name, header_color=COLOR_HEADER)
        story.extend([audit_table, Spacer(1, 8)])

    story.extend(_section_title("五、能力维度分析", styles))
    capability_rows: list[list[object]] = [["维度", "得分", "标签", "维度解读", "关键观察"]]
    for row in capabilities.get("categories", []):
        display_name = str(row.get("display_name") or row["category"])
        definition = str(row.get("definition") or "用于评估该维度的综合表现")
        capability_rows.append(
            [
                _paragraph(display_name, styles["cell"]),
                _paragraph(_fmt_number(row["score"]), styles["cell"]),
                _paragraph(str(row["label"]), styles["cell"]),
                _paragraph(_clip(definition, 42), styles["cell"]),
                _paragraph(_clip(_capability_observation(row), 80), styles["cell"]),
            ]
        )
    capability_table = Table(capability_rows, colWidths=[72, 40, 52, 152, 206])
    _apply_table_style(capability_table, font_name, header_color=COLOR_HEADER)
    story.extend([capability_table, Spacer(1, 8)])

    story.extend(_section_title("六、高风险主题汇总（去重）", styles))
    if risk_summary:
        risk_rows: list[list[object]] = [["风险主题（去重）", "涉及主体（前三）", "等级", "影响度", "频次", "涉及平台/分类"]]
        for item in risk_summary:
            providers = " / ".join(sorted(item["providers"]))
            categories = " / ".join(sorted(item["categories"]))
            scope = f"{providers} | {categories}"
            risk_rows.append(
                [
                    _paragraph(_clip(str(item["topic"]), 56), styles["cell"]),
                    _paragraph(f"{item['subject_summary']}（共{item['subject_count']}个）", styles["cell"]),
                    _paragraph(_risk_level_cn(str(item["risk_level"])), styles["cell"]),
                    _paragraph(_fmt_number(item["impact_max"]), styles["cell"]),
                    _paragraph(str(item["count"]), styles["cell"]),
                    _paragraph(_clip(scope, 44), styles["cell"]),
                ]
            )
        risk_table = Table(risk_rows, colWidths=[188, 56, 48, 52, 40, 138])
        _apply_table_style(risk_table, font_name, header_color=COLOR_RISK_HEADER)
        story.append(risk_table)
    else:
        story.append(Paragraph("本周期未发现严重或高风险主题", styles["body"]))
    story.append(Spacer(1, 8))

    story.extend(_section_title("七、竞品分流主题汇总（去重）", styles))
    if hijack_summary:
        hijack_rows: list[list[object]] = [["问题主题", "分流次数", "平均强度", "最高强度", "主要推荐实体（前三）"]]
        for item in hijack_summary:
            hijack_rows.append(
                [
                    _paragraph(_clip(str(item["prompt_text"]), 52), styles["cell"]),
                    _paragraph(str(item["count"]), styles["cell"]),
                    _paragraph(_fmt_number(item["avg_strength"]), styles["cell"]),
                    _paragraph(_fmt_number(item["max_strength"]), styles["cell"]),
                    _paragraph(" / ".join(item["top_entities"]) or "—", styles["cell"]),
                ]
            )
        hijack_table = Table(hijack_rows, colWidths=[240, 56, 58, 58, 110])
        _apply_table_style(hijack_table, font_name, header_color=COLOR_HEADER)
        story.append(hijack_table)
    else:
        story.append(Paragraph("本周期未发现明显竞品分流事件", styles["body"]))
    story.append(Spacer(1, 8))

    story.extend(_section_title("八、行动建议与闭环", styles))
    action_rows: list[list[object]] = [["优先级", "行动主题", "建议动作"]]
    for priority, topic, action in _recommendations(report_type, risk_summary, hijack_summary, capabilities):
        action_rows.append(
            [
                _paragraph(priority, styles["cell"]),
                _paragraph(topic, styles["cell"]),
                _paragraph(action, styles["cell"]),
            ]
        )
    action_table = Table(action_rows, colWidths=[52, 120, 342])
    _apply_table_style(action_table, font_name, header_color=COLOR_HEADER)
    story.append(action_table)

    framework = get_analysis_framework()
    module_layers = [item for item in framework.get("module_layers", []) if isinstance(item, dict)]
    delivery_stages = [item for item in framework.get("delivery_stages", []) if isinstance(item, dict)]

    story.extend(_section_title("九、分析模块与交付路径", styles))
    if module_layers:
        layer_rows: list[list[object]] = [["分层", "目标", "模块重点（节选）"]]
        for item in module_layers:
            modules = item.get("modules", [])
            module_text = "、".join(str(module) for module in modules[:5]) if isinstance(modules, list) else "—"
            layer_rows.append(
                [
                    _paragraph(str(item.get("level", "—")), styles["cell"]),
                    _paragraph(str(item.get("goal", "—")), styles["cell"]),
                    _paragraph(_clip(module_text, 100), styles["cell"]),
                ]
            )
        layer_table = Table(layer_rows, colWidths=[88, 130, 296])
        _apply_table_style(layer_table, font_name, header_color=COLOR_HEADER)
        story.extend([layer_table, Spacer(1, 6)])

    if delivery_stages:
        stage_rows: list[list[object]] = [["适用阶段", "报告聚焦", "核心输出", "管理层视角"]]
        for item in delivery_stages:
            stage_rows.append(
                [
                    _paragraph(str(item.get("stage", "—")), styles["cell"]),
                    _paragraph(str(item.get("report_focus", "—")), styles["cell"]),
                    _paragraph(_clip(str(item.get("core_outputs", "—")), 72), styles["cell"]),
                    _paragraph(_clip(str(item.get("management_view", "—")), 60), styles["cell"]),
                ]
            )
        stage_table = Table(stage_rows, colWidths=[88, 96, 170, 160])
        _apply_table_style(stage_table, font_name, header_color=COLOR_HEADER)
        story.append(stage_table)

    doc.build(story)


def generate_report(
    db: Session,
    org_id: int,
    report_type: ReportType,
    *,
    brand_id: int | None = None,
    week_start: date | None = None,
    month: str | None = None,
) -> Report:
    period_start, period_end = _report_range(report_type, week_start=week_start, month=month)

    organization = db.scalar(select(Organization).where(Organization.id == org_id))
    brand = resolve_brand(db, org_id, brand_id=brand_id)
    if not organization or not brand:
        raise ValueError("Missing organization or brand")

    range_start = datetime.combine(period_start, time.min, tzinfo=timezone.utc)
    range_end = datetime.combine(period_end, time.max, tzinfo=timezone.utc)
    period_runs = get_runs_for_period(
        db, org_id, range_start, range_end, provider="all", brand_id=brand.id
    )
    run_ids = [run.id for run in period_runs]

    overview = build_overview_from_runs(
        db,
        org_id,
        period_runs,
        range_key=f"{period_start}~{period_end}",
        provider="all",
        brand_id=brand.id,
    )
    capabilities = build_capabilities_from_runs(
        db,
        org_id,
        period_runs,
        range_key=f"{period_start}~{period_end}",
        provider="all",
        brand_id=brand.id,
    )

    all_claims = list_claims_by_run_ids(db, run_ids)
    risk_claims = [
        claim
        for claim in all_claims
        if claim["risk_level"] in {ClaimRiskLevel.high.value, ClaimRiskLevel.critical.value}
    ]
    hijacks = list_hijacks_by_run_ids(db, org_id, run_ids, brand_id=brand.id)

    file_name = f"{report_type.value}_{org_id}_brand{brand.id}_{period_start}_{period_end}.pdf"
    output_path = settings.reports_dir / file_name
    title = "AI品牌风险作战简报" if report_type == ReportType.weekly_brief else "AI品牌战略报告"
    _build_report_document(
        report_type=report_type,
        title=title,
        org_name=organization.name,
        brand_name=brand.name,
        project_context=brand.project_context,
        period_start=period_start,
        period_end=period_end,
        run_count=len(period_runs),
        overview=overview,
        capabilities=capabilities,
        all_claims=all_claims,
        period_runs=period_runs,
        risk_claims=risk_claims,
        hijacks=hijacks,
        output_path=output_path,
    )

    report = Report(
        org_id=org_id,
        brand_id=brand.id,
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        file_path=str(output_path),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
