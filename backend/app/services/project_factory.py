from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from sqlalchemy import delete as sa_delete, select
from sqlalchemy.orm import Session

from app.core.enums import PromptCategory, PromptIntentType

if TYPE_CHECKING:
    from app.models import Brand

MAX_COMPETITORS_PER_BRAND = 12
DEFAULT_AUTO_COMPETITOR_COUNT = 3
CUSTOM_INDUSTRY = "其他（自定义）"

INDUSTRY_OPTIONS = [
    "跨境贸易与服务",
    "跨境电商",
    "新能源车",
    "营销服务",
    "医疗器械",
    "金融服务",
    "SaaS企业软件",
    "物流供应链",
    "消费电子",
    "教育服务",
    "专业服务",
    "通用行业",
]

_BUCKET_TO_DISPLAY = {
    "香港跨境服务": "跨境贸易与服务",
    "跨境电商": "跨境电商",
    "新能源车": "新能源车",
    "营销服务": "营销服务",
    "医疗器械": "医疗器械",
    "金融服务": "金融服务",
    "SaaS企业软件": "SaaS企业软件",
    "物流供应链": "物流供应链",
    "消费电子": "消费电子",
    "教育服务": "教育服务",
    "专业服务": "专业服务",
    "通用行业": "通用行业",
}

_INDUSTRY_TO_BUCKET = {
    "跨境贸易与服务": "香港跨境服务",
    "跨境电商": "跨境电商",
    "新能源车": "新能源车",
    "汽车与出行": "新能源车",
    "营销服务": "营销服务",
    "医疗器械": "医疗器械",
    "医疗健康": "医疗器械",
    "金融服务": "金融服务",
    "SaaS企业软件": "SaaS企业软件",
    "互联网与软件": "SaaS企业软件",
    "物流供应链": "物流供应链",
    "消费电子": "消费电子",
    "零售消费": "消费电子",
    "教育服务": "教育服务",
    "专业服务": "专业服务",
    "工业制造": "通用行业",
    "能源与公用事业": "新能源车",
    "通用行业": "通用行业",
}

_INDUSTRY_SYNONYMS = {
    "香港跨境服务": ("跨境", "香港", "离岸", "公司注册", "税务", "秘书服务", "海外主体"),
    "跨境电商": ("跨境电商", "出海电商", "temu", "amazon", "亚马逊", "shopify", "shopee", "独立站"),
    "新能源车": (
        "新能源",
        "电动车",
        "智能汽车",
        "ev",
        "汽车",
        "比亚迪",
        "特斯拉",
        "蔚来",
        "理想",
        "小鹏",
        "byd",
        "tesla",
        "nio",
        "xpeng",
    ),
    "医疗器械": ("医疗器械", "ivd", "影像设备", "医用设备", "医疗", "医院", "诊断", "器械"),
    "营销服务": (
        "营销",
        "广告",
        "投放",
        "媒介",
        "品牌传播",
        "数字营销",
        "整合营销",
        "公关传播",
        "增长",
        "私域",
        "内容营销",
        "广告代理",
    ),
    "金融服务": ("金融", "银行", "证券", "保险", "支付", "财富管理", "投行"),
    "SaaS企业软件": ("saas", "crm", "erp", "企业软件", "云服务", "软件", "系统集成", "数字化"),
    "物流供应链": ("物流", "供应链", "仓储", "货运", "快递", "履约", "运输"),
    "消费电子": ("消费电子", "手机", "硬件", "可穿戴", "终端", "家电", "数码"),
    "教育服务": ("教育", "培训", "学习", "留学", "教培", "课程", "职业教育"),
    "专业服务": ("咨询", "律所", "会计", "审计", "服务商", "顾问"),
}

_INDUSTRY_COMPETITOR_CATALOG: dict[str, list[tuple[str, str]]] = {
    "香港跨境服务": [
        ("卓佳Tricor", "香港公司治理与秘书服务头部机构"),
        ("瑞丰德永", "跨境公司注册与财税服务机构"),
        ("德勤Deloitte", "大型综合专业服务机构"),
        ("安永EY", "企业合规与审计咨询机构"),
        ("毕马威KPMG", "跨境税务与合规服务机构"),
        ("普华永道PwC", "企业财税与咨询服务机构"),
    ],
    "跨境电商": [
        ("亚马逊", "全球跨境电商平台"),
        ("Temu", "高速增长的跨境电商平台"),
        ("速卖通", "阿里系跨境平台"),
        ("SHEIN", "跨境DTC品牌与平台生态"),
        ("Lazada", "东南亚电商平台"),
        ("Shopee", "东南亚电商平台"),
        ("eBay", "成熟跨境交易平台"),
        ("Shopify", "跨境独立站电商基础设施"),
    ],
    "新能源车": [
        ("特斯拉", "全球新能源车头部品牌"),
        ("蔚来", "中国中高端新能源车品牌"),
        ("小鹏汽车", "智能电动车品牌"),
        ("理想汽车", "增程与家庭新能源车品牌"),
        ("极氪", "高端智能新能源品牌"),
        ("广汽埃安", "规模化新能源车品牌"),
        ("零跑汽车", "智能新能源车品牌"),
        ("问界", "智能汽车新势力品牌"),
    ],
    "医疗器械": [
        ("迈瑞医疗", "中国医疗器械头部品牌"),
        ("联影医疗", "医学影像设备头部品牌"),
        ("鱼跃医疗", "家用医疗设备品牌"),
        ("美敦力Medtronic", "国际医疗器械龙头"),
        ("强生医疗", "综合医疗科技公司"),
        ("西门子医疗", "医疗影像与诊断设备企业"),
        ("GE医疗", "全球医疗设备企业"),
        ("飞利浦医疗", "医疗影像与监护设备企业"),
    ],
    "营销服务": [
        ("蓝色光标", "数字营销与品牌传播服务机构"),
        ("省广集团", "综合广告与营销服务集团"),
        ("华扬联众", "数字营销与媒介服务机构"),
        ("分众传媒", "品牌传播与媒介平台"),
        ("奥美Ogilvy", "国际品牌营销服务机构"),
        ("阳狮Publicis", "国际整合营销服务机构"),
        ("WPP群邑", "国际媒介与营销服务集团"),
        ("电通Dentsu", "国际广告与传播服务机构"),
    ],
    "金融服务": [
        ("招商银行", "零售与企业金融服务机构"),
        ("平安银行", "综合金融服务机构"),
        ("蚂蚁集团", "数字支付与普惠金融平台"),
        ("腾讯金融", "互联网金融服务平台"),
        ("中信证券", "综合证券服务机构"),
        ("华泰证券", "头部证券机构"),
        ("高盛Goldman Sachs", "国际投行与资管机构"),
        ("摩根士丹利Morgan Stanley", "国际投行与财富管理机构"),
    ],
    "SaaS企业软件": [
        ("Salesforce", "全球CRM SaaS头部厂商"),
        ("Microsoft Dynamics", "企业级CRM与ERP平台"),
        ("HubSpot", "营销销售一体化SaaS平台"),
        ("Zoho", "中小企业SaaS工具套件"),
        ("金蝶", "企业管理软件厂商"),
        ("用友", "企业服务软件厂商"),
        ("纷享销客", "国内CRM SaaS厂商"),
        ("销售易", "国内CRM SaaS厂商"),
    ],
    "物流供应链": [
        ("顺丰", "综合物流服务商"),
        ("京东物流", "仓配一体化物流服务商"),
        ("菜鸟", "电商物流网络平台"),
        ("中外运", "综合供应链与物流服务商"),
        ("DHL", "国际快递与供应链服务商"),
        ("FedEx", "国际物流服务商"),
        ("UPS", "国际快递物流服务商"),
        ("德迅Kuehne+Nagel", "全球供应链服务商"),
    ],
    "消费电子": [
        ("华为", "全球消费电子品牌"),
        ("小米", "消费电子与智能硬件品牌"),
        ("苹果Apple", "全球高端消费电子品牌"),
        ("三星Samsung", "全球消费电子品牌"),
        ("OPPO", "消费电子品牌"),
        ("vivo", "消费电子品牌"),
        ("荣耀HONOR", "智能终端品牌"),
        ("联想Lenovo", "消费电子与PC品牌"),
    ],
    "教育服务": [
        ("新东方", "综合教育服务机构"),
        ("高途", "在线教育服务机构"),
        ("学而思", "K12教育品牌"),
        ("网易有道", "在线学习产品品牌"),
        ("沪江", "在线学习平台"),
        ("Udemy", "国际在线课程平台"),
        ("Coursera", "国际课程与证书平台"),
        ("可汗学院Khan Academy", "公益教育平台"),
    ],
    "专业服务": [
        ("麦肯锡McKinsey", "管理咨询机构"),
        ("BCG波士顿咨询", "战略咨询机构"),
        ("贝恩Bain", "战略咨询机构"),
        ("埃森哲Accenture", "咨询与技术服务机构"),
        ("德勤咨询", "综合咨询机构"),
        ("安永咨询", "综合咨询机构"),
        ("毕马威咨询", "综合咨询机构"),
        ("普华永道咨询", "综合咨询机构"),
    ],
    "通用行业": [
        ("麦肯锡McKinsey", "管理咨询与战略服务机构"),
        ("BCG波士顿咨询", "全球战略咨询机构"),
        ("埃森哲Accenture", "咨询与数字化服务机构"),
        ("德勤咨询", "综合咨询服务机构"),
        ("安永咨询", "综合咨询服务机构"),
        ("普华永道咨询", "综合咨询服务机构"),
        ("毕马威咨询", "综合咨询服务机构"),
        ("贝恩Bain", "管理咨询机构"),
    ],
}

_PLACEHOLDER_COMPETITOR_NAMES = {
    "竞品A",
    "竞品B",
    "竞品C",
    "同类品牌1",
    "同类品牌2",
    "同类品牌3",
    "领航优选",
    "星图服务",
    "睿策咨询",
    "卓信方案",
    "明略伙伴",
    "启衡顾问",
    "合壹服务",
    "远见咨询",
    "博远优选",
    "云策伙伴",
    "智研顾问",
    "鼎衡服务",
}

_QUERY_ALIAS_MAP = {
    "tesla": "特斯拉",
    "byd": "比亚迪",
    "nio": "蔚来",
    "xpeng": "小鹏汽车",
    "li auto": "理想汽车",
    "zeekr": "极氪",
    "medtronic": "美敦力Medtronic",
    "salesforce": "Salesforce",
}


def normalize_brand_aliases(brand_name: str, aliases: Iterable[str] | None = None) -> list[str]:
    tokens: list[str] = []
    for value in [brand_name, *list(aliases or [])]:
        cleaned = (value or "").strip()
        if cleaned:
            tokens.append(cleaned)

    expanded = list(tokens)
    for token in tokens:
        token_lower = token.lower()
        for alias, canonical in _QUERY_ALIAS_MAP.items():
            if alias in token_lower:
                expanded.append(canonical)
            if canonical.lower() in token_lower:
                expanded.append(alias.upper() if alias.isascii() and alias.isalpha() and len(alias) <= 6 else alias)

    deduped: list[str] = []
    seen: set[str] = set()
    for token in expanded:
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(token)

    brand_lower = (brand_name or "").strip().lower()
    return [token for token in deduped if token.lower() != brand_lower]


def industry_options() -> list[str]:
    return [*INDUSTRY_OPTIONS, CUSTOM_INDUSTRY]


def normalize_project_context(project_context: str | None) -> str:
    context = (project_context or "").strip()
    if not context:
        return "通用行业"
    if context in INDUSTRY_OPTIONS:
        return context
    if context in _BUCKET_TO_DISPLAY:
        return _BUCKET_TO_DISPLAY[context]
    if context in _INDUSTRY_TO_BUCKET:
        return _BUCKET_TO_DISPLAY.get(_INDUSTRY_TO_BUCKET[context], "通用行业")

    context_lower = context.lower()
    for industry, keywords in _INDUSTRY_SYNONYMS.items():
        if any(keyword.lower() in context_lower for keyword in keywords):
            return _BUCKET_TO_DISPLAY.get(industry, industry)
    return context


def infer_project_context(
    brand_name: str,
    project_context: str | None,
    aliases: Iterable[str] | None = None,
) -> str:
    context = normalize_project_context(project_context)
    if context != "通用行业":
        return context

    signals = [(brand_name or "").strip(), *[(item or "").strip() for item in (aliases or [])]]
    normalized_signals = [token.lower() for token in signals if token]
    if not normalized_signals:
        return context

    expanded_signals = list(normalized_signals)
    for token in normalized_signals:
        for alias, canonical in _QUERY_ALIAS_MAP.items():
            if alias in token:
                expanded_signals.append(canonical.lower())

    for industry, keywords in _INDUSTRY_SYNONYMS.items():
        normalized_keywords = [keyword.lower() for keyword in keywords]
        if any(keyword in token for token in expanded_signals for keyword in normalized_keywords):
            return industry

    for industry, candidates in _INDUSTRY_COMPETITOR_CATALOG.items():
        for candidate_name, _ in candidates:
            target = candidate_name.strip().lower()
            if len(target) < 2:
                continue
            if any(token in target or target in token for token in expanded_signals):
                return industry
    return context


def resolve_industry_bucket(project_context: str | None) -> str:
    context = normalize_project_context(project_context)
    context_lower = context.lower()
    if context in _INDUSTRY_TO_BUCKET:
        return _INDUSTRY_TO_BUCKET[context]
    if context in _INDUSTRY_COMPETITOR_CATALOG:
        return context

    for industry, keywords in _INDUSTRY_SYNONYMS.items():
        if any(keyword in context_lower for keyword in keywords):
            return industry
    return "通用行业"


def _looks_same_brand(brand_name: str, candidate: str) -> bool:
    source = brand_name.strip()
    target = candidate.strip()
    if not source or not target:
        return False
    source_tokens = brand_identity_tokens(source)
    target_tokens = brand_identity_tokens(target)
    if source_tokens & target_tokens:
        return True
    source_lower = source.lower()
    target_lower = target.lower()
    return source_lower in target_lower or target_lower in source_lower


def _competitor_aliases(name: str) -> list[str]:
    base = (
        name.replace("咨询", "")
        .replace("服务", "")
        .replace("顾问", "")
        .replace("集团", "")
        .replace("公司", "")
        .replace("品牌", "")
        .replace(" ", "")
    )
    aliases = [base[:4], base[:2]]
    deduped: list[str] = []
    for alias in aliases:
        if alias and alias not in deduped:
            deduped.append(alias)
    return deduped


def recommend_real_competitors(
    brand_name: str,
    project_context: str | None = None,
    limit: int = 8,
) -> list[dict[str, object]]:
    bucket = resolve_industry_bucket(project_context)
    catalog = _INDUSTRY_COMPETITOR_CATALOG.get(bucket, _INDUSTRY_COMPETITOR_CATALOG["通用行业"])

    suggestions: list[dict[str, object]] = []
    seen: set[str] = set()
    for candidate_name, reason in catalog:
        if _looks_same_brand(brand_name, candidate_name):
            continue
        if candidate_name in seen:
            continue
        suggestions.append(
            {
                "name": candidate_name,
                "aliases": _competitor_aliases(candidate_name),
                "reason": reason,
                "industry": bucket,
            }
        )
        seen.add(candidate_name)
        if len(suggestions) >= limit:
            break
    return suggestions


def search_real_competitors(
    brand_name: str,
    query: str | None = None,
    project_context: str | None = None,
    limit: int = 12,
) -> list[dict[str, object]]:
    query_text = (query or "").strip().lower()
    if not query_text:
        return recommend_real_competitors(brand_name, project_context, limit=limit)

    bucket = resolve_industry_bucket(project_context)
    expanded_queries = [query_text]
    for alias, canonical in _QUERY_ALIAS_MAP.items():
        if alias in query_text:
            expanded_queries.append(canonical.lower())

    token_set: set[str] = set()
    for item in expanded_queries:
        for token in item.replace("，", " ").replace(",", " ").split():
            token = token.strip()
            if token:
                token_set.add(token)
    tokens = list(token_set)

    pool: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for industry, items in _INDUSTRY_COMPETITOR_CATALOG.items():
        for candidate_name, reason in items:
            if candidate_name in seen:
                continue
            seen.add(candidate_name)
            pool.append((industry, candidate_name, reason))

    scored: list[tuple[int, str, str, str]] = []
    for industry, candidate_name, reason in pool:
        if _looks_same_brand(brand_name, candidate_name):
            continue
        name_lower = candidate_name.lower()
        reason_lower = reason.lower()
        score = 0
        if industry == bucket:
            score += 3
        if any(candidate in name_lower for candidate in expanded_queries):
            score += 5
        if any(candidate in reason_lower for candidate in expanded_queries):
            score += 2
        for token in tokens:
            if token in name_lower:
                score += 2
            if token in reason_lower:
                score += 1
        if score > 0:
            scored.append((score, industry, candidate_name, reason))

    if not scored:
        return recommend_real_competitors(brand_name, project_context, limit=limit)

    scored.sort(key=lambda item: (-item[0], item[1] != bucket, item[2]))
    results: list[dict[str, object]] = []
    for _, industry, candidate_name, reason in scored[: max(limit, 1)]:
        results.append(
            {
                "name": candidate_name,
                "aliases": _competitor_aliases(candidate_name),
                "reason": reason,
                "industry": industry,
            }
        )
    return results


def generate_competitor_profiles(
    brand_name: str,
    project_context: str | None = None,
    limit: int = DEFAULT_AUTO_COMPETITOR_COUNT,
) -> list[tuple[str, list[str]]]:
    return [
        (item["name"], item["aliases"])  # type: ignore[index]
        for item in recommend_real_competitors(brand_name, project_context, limit=limit)
    ]


def _prompt_templates() -> list[tuple[PromptCategory, PromptIntentType, str]]:
    return [
        (PromptCategory.fee, PromptIntentType.fee, "在{scene}场景里，{brand}的报价透明吗，会不会后期加价？"),
        (PromptCategory.fee, PromptIntentType.fee, "选择{brand}前，通常要确认哪些收费项？"),
        (PromptCategory.fee, PromptIntentType.comparison, "{brand}和同类品牌相比，总成本高还是低？"),
        (PromptCategory.fee, PromptIntentType.selection, "预算有限时，优先选{brand}是否划算？"),
        (PromptCategory.fee, PromptIntentType.complaint, "用户对{brand}的价格投诉主要集中在哪些点？"),
        (PromptCategory.fee, PromptIntentType.risk, "{brand}是否存在隐形收费或合同外费用风险？"),
        (PromptCategory.fee, PromptIntentType.selection, "在{scene}合作中，{brand}的性价比表现怎么样？"),
        (PromptCategory.fee, PromptIntentType.comparison, "长期合作看，{brand}的成本可控性相比竞品如何？"),
        (PromptCategory.expertise, PromptIntentType.selection, "{brand}在{scene}领域的专业能力属于什么水平？"),
        (PromptCategory.expertise, PromptIntentType.comparison, "如果场景复杂，{brand}和主要竞品谁更专业？"),
        (PromptCategory.expertise, PromptIntentType.selection, "{brand}是否擅长复杂问题排查和方案落地？"),
        (PromptCategory.expertise, PromptIntentType.complaint, "用户对{brand}专业能力最常见的负面反馈是什么？"),
        (PromptCategory.expertise, PromptIntentType.risk, "选择{brand}做关键项目，专业能力上有哪些风险点？"),
        (PromptCategory.expertise, PromptIntentType.selection, "{brand}的顾问团队是否有可验证的行业经验？"),
        (PromptCategory.expertise, PromptIntentType.comparison, "与替代品牌相比，{brand}在方案质量上是否更有优势？"),
        (PromptCategory.expertise, PromptIntentType.selection, "综合口碑看，{brand}在{scene}的专业可信度如何？"),
        (PromptCategory.success, PromptIntentType.selection, "{brand}在{scene}项目里的结果达成率怎么样？"),
        (PromptCategory.success, PromptIntentType.comparison, "{brand}和同类品牌相比，项目成功率谁更稳定？"),
        (PromptCategory.success, PromptIntentType.risk, "选择{brand}时，哪些情况最容易导致结果不达预期？"),
        (PromptCategory.success, PromptIntentType.selection, "{brand}是否有成熟的预审机制来提高成功率？"),
        (PromptCategory.success, PromptIntentType.complaint, "围绕{brand}的成功率，用户最常见争议是什么？"),
        (PromptCategory.success, PromptIntentType.selection, "时间紧任务下，{brand}的交付达成率是否可靠？"),
        (PromptCategory.success, PromptIntentType.comparison, "{brand}与竞品相比，谁更容易一次性交付成功？"),
        (PromptCategory.success, PromptIntentType.selection, "在高难度项目里，{brand}的稳定性值得信赖吗？"),
        (PromptCategory.efficiency, PromptIntentType.selection, "{brand}在{scene}项目的响应和推进速度如何？"),
        (PromptCategory.efficiency, PromptIntentType.comparison, "{brand}与主要替代品牌相比，谁的响应更快？"),
        (PromptCategory.efficiency, PromptIntentType.risk, "使用{brand}时，哪些环节最容易拖期？"),
        (PromptCategory.efficiency, PromptIntentType.selection, "{brand}的资料清单和流程指引是否清晰高效？"),
        (PromptCategory.efficiency, PromptIntentType.complaint, "用户对{brand}时效问题最常见的吐槽有哪些？"),
        (PromptCategory.efficiency, PromptIntentType.selection, "周期很紧时，{brand}是否适合快速上线项目？"),
        (PromptCategory.efficiency, PromptIntentType.comparison, "与竞品相比，{brand}谁更能缩短交付周期？"),
        (PromptCategory.efficiency, PromptIntentType.selection, "跨团队协作下，{brand}的推进效率是否稳定？"),
        (PromptCategory.compliance, PromptIntentType.selection, "{brand}的合规管理流程是否规范可靠？"),
        (PromptCategory.compliance, PromptIntentType.risk, "选择{brand}时，合规与风险控制需要重点核查哪些点？"),
        (PromptCategory.compliance, PromptIntentType.comparison, "{brand}与替代品牌相比，谁的合规能力更强？"),
        (PromptCategory.compliance, PromptIntentType.complaint, "{brand}在合规服务上最常见的投诉是什么？"),
        (PromptCategory.compliance, PromptIntentType.selection, "{brand}的合同条款和风险提示是否完整清晰？"),
        (PromptCategory.compliance, PromptIntentType.risk, "如果非常重视监管要求，选择{brand}有哪些潜在风险？"),
        (PromptCategory.compliance, PromptIntentType.selection, "{brand}是否具备可复核的合规流程与证据链？"),
        (PromptCategory.compliance, PromptIntentType.comparison, "{brand}与行业头部品牌相比，谁在风险预警上更成熟？"),
        (PromptCategory.experience, PromptIntentType.selection, "{brand}的整体服务体验和售后支持怎么样？"),
        (PromptCategory.experience, PromptIntentType.comparison, "{brand}和竞品相比，谁的客户体验更好？"),
        (PromptCategory.experience, PromptIntentType.complaint, "{brand}在服务体验方面最容易被诟病的问题是什么？"),
        (PromptCategory.experience, PromptIntentType.selection, "{brand}的沟通透明度和跟进质量是否稳定？"),
        (PromptCategory.experience, PromptIntentType.risk, "如果担心服务中断，选择{brand}有哪些体验风险？"),
        (PromptCategory.experience, PromptIntentType.selection, "需要长期陪跑时，{brand}是否值得选？"),
        (PromptCategory.experience, PromptIntentType.comparison, "与主要替代方案相比，{brand}是否更省心？"),
        (PromptCategory.experience, PromptIntentType.selection, "从复购用户反馈看，{brand}的满意度如何？"),
        (PromptCategory.expertise, PromptIntentType.comparison, "综合来看，在{scene}场景下{brand}与主要竞品谁更值得优先推荐？"),
        (PromptCategory.compliance, PromptIntentType.risk, "如果要避免踩坑，在{scene}项目中选择{brand}需要重点关注哪些风险点？"),
    ]


def generate_project_prompts(
    brand_name: str,
    project_context: str | None = None,
) -> list[dict[str, PromptCategory | PromptIntentType | str]]:
    scene = normalize_project_context(project_context)
    return [
        {
            "text": template.format(brand=brand_name, scene=scene),
            "category": category,
            "intent_type": intent,
        }
        for category, intent, template in _prompt_templates()
    ]


def _existing_competitor_names(db: Session, org_id: int, brand_id: int) -> set[str]:
    from app.models import Competitor

    db.flush()
    return {
        item.name.strip().lower()
        for item in db.scalars(
            select(Competitor).where(Competitor.org_id == org_id, Competitor.brand_id == brand_id)
        )
    }


def replace_placeholder_competitors(db: Session, org_id: int, brand: "Brand") -> None:
    from app.models import Competitor

    competitors = list(
        db.scalars(
            select(Competitor)
            .where(Competitor.org_id == org_id, Competitor.brand_id == brand.id)
            .order_by(Competitor.id.asc())
        )
    )
    if not competitors:
        return

    suggestions = recommend_real_competitors(
        brand.name,
        brand.project_context,
        limit=max(len(competitors), DEFAULT_AUTO_COMPETITOR_COUNT) + 4,
    )
    suggestion_names = [item["name"] for item in suggestions]
    used_names = {item.name.lower() for item in competitors if item.name not in _PLACEHOLDER_COMPETITOR_NAMES}
    suggestion_index = 0
    for competitor in competitors:
        if competitor.name not in _PLACEHOLDER_COMPETITOR_NAMES:
            continue
        while (
            suggestion_index < len(suggestion_names)
            and suggestion_names[suggestion_index].lower() in used_names
        ):
            suggestion_index += 1
        if suggestion_index >= len(suggestion_names):
            break
        new_name = suggestion_names[suggestion_index]
        competitor.name = new_name
        competitor.aliases = _competitor_aliases(new_name)
        used_names.add(new_name.lower())
        suggestion_index += 1

    for competitor in competitors:
        if competitor.name in _PLACEHOLDER_COMPETITOR_NAMES and len(used_names) >= DEFAULT_AUTO_COMPETITOR_COUNT:
            db.delete(competitor)


def _create_missing_competitors(
    db: Session,
    org_id: int,
    brand: "Brand",
    competitor_names: Iterable[str] | None = None,
) -> None:
    from app.models import Competitor

    existing = _existing_competitor_names(db, org_id, brand.id)
    requested = [name.strip() for name in (competitor_names or []) if name.strip()]
    if not requested:
        requested = [
            item["name"]  # type: ignore[index]
            for item in recommend_real_competitors(
                brand.name,
                brand.project_context,
                limit=DEFAULT_AUTO_COMPETITOR_COUNT,
            )
        ]

    for name in requested:
        if len(existing) >= MAX_COMPETITORS_PER_BRAND:
            break
        lowered_name = name.lower()
        if lowered_name in existing or _looks_same_brand(brand.name, name):
            continue
        db.add(
            Competitor(
                org_id=org_id,
                brand_id=brand.id,
                name=name,
                aliases=_competitor_aliases(name),
            )
        )
        existing.add(lowered_name)


def _ensure_prompt_library(db: Session, org_id: int, brand: "Brand") -> None:
    from app.models import Prompt

    prompts = list(
        db.scalars(
            select(Prompt)
            .where(Prompt.org_id == org_id, Prompt.brand_id == brand.id)
            .order_by(Prompt.id.asc())
        )
    )
    active_prompts = [prompt for prompt in prompts if prompt.is_active]
    expected_prompts = generate_project_prompts(brand.name, brand.project_context)

    if len(active_prompts) == len(expected_prompts):
        aligned = True
        for prompt, expected in zip(active_prompts, expected_prompts):
            if (
                prompt.text != expected["text"]
                or prompt.category != expected["category"]
                or prompt.intent_type != expected["intent_type"]
            ):
                aligned = False
                break
        if aligned:
            return

    for prompt in active_prompts:
        prompt.is_active = False

    for prompt in expected_prompts:
        db.add(
            Prompt(
                org_id=org_id,
                brand_id=brand.id,
                text=prompt["text"],
                category=prompt["category"],
                intent_type=prompt["intent_type"],
                is_active=True,
            )
        )


def _normalize_identity_token(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or "\u4e00" <= ch <= "\u9fff")


def brand_identity_tokens(brand_name: str, aliases: Iterable[str] | None = None) -> set[str]:
    tokens = [brand_name, *normalize_brand_aliases(brand_name, aliases)]
    identities: set[str] = set()
    for token in tokens:
        normalized = _normalize_identity_token(token.strip())
        if not normalized:
            continue
        identities.add(normalized)
        for alias, canonical in _QUERY_ALIAS_MAP.items():
            alias_key = _normalize_identity_token(alias)
            canonical_key = _normalize_identity_token(canonical)
            if alias_key and alias_key in normalized:
                identities.add(canonical_key)
            if canonical_key and canonical_key in normalized:
                identities.add(alias_key)
    return identities


def _dedupe_active_prompts(db: Session, org_id: int, brand_id: int) -> None:
    from app.models import Prompt

    prompts = list(
        db.scalars(
            select(Prompt)
            .where(Prompt.org_id == org_id, Prompt.brand_id == brand_id)
            .order_by(Prompt.id.asc())
        )
    )
    seen_active: set[tuple[str, str, str]] = set()
    for prompt in prompts:
        key = (
            prompt.text.strip(),
            prompt.category.value if hasattr(prompt.category, "value") else str(prompt.category),
            prompt.intent_type.value if hasattr(prompt.intent_type, "value") else str(prompt.intent_type),
        )
        if prompt.is_active and key in seen_active:
            prompt.is_active = False
            continue
        if prompt.is_active:
            seen_active.add(key)


def _replace_misaligned_competitors(db: Session, org_id: int, brand: "Brand") -> None:
    from app.models import Competitor

    bucket = resolve_industry_bucket(brand.project_context)
    if bucket == "通用行业":
        return

    competitors = list(
        db.scalars(
            select(Competitor)
            .where(Competitor.org_id == org_id, Competitor.brand_id == brand.id)
            .order_by(Competitor.id.asc())
        )
    )
    if not competitors:
        return

    generic_names = {name for name, _ in _INDUSTRY_COMPETITOR_CATALOG["通用行业"]}
    bucket_names = {name for name, _ in _INDUSTRY_COMPETITOR_CATALOG.get(bucket, [])}
    recognized_by_bucket: dict[str, set[str]] = {}
    for industry, catalog in _INDUSTRY_COMPETITOR_CATALOG.items():
        for candidate_name, _ in catalog:
            key = candidate_name.strip().lower()
            if not key:
                continue
            recognized_by_bucket.setdefault(key, set()).add(industry)

    kept_count = 0
    removed = False
    for item in competitors:
        item_name = item.name.strip()
        item_key = item_name.lower()
        if (
            item_name in _PLACEHOLDER_COMPETITOR_NAMES
            or _looks_same_brand(brand.name, item_name)
            or item_name in generic_names
        ):
            db.delete(item)
            removed = True
            continue

        if item_name in bucket_names:
            kept_count += 1
            continue

        matched_buckets = set(recognized_by_bucket.get(item_key, set()))
        matched_buckets.discard("通用行业")
        if matched_buckets and bucket not in matched_buckets:
            db.delete(item)
            removed = True
            continue
        kept_count += 1

    if removed:
        db.flush()
    if kept_count < DEFAULT_AUTO_COMPETITOR_COUNT:
        _create_missing_competitors(db, org_id, brand, competitor_names=None)


def _dedupe_competitors(db: Session, org_id: int, brand: "Brand") -> None:
    from app.models import Competitor

    competitors = list(
        db.scalars(
            select(Competitor)
            .where(Competitor.org_id == org_id, Competitor.brand_id == brand.id)
            .order_by(Competitor.id.asc())
        )
    )
    seen_names: set[str] = set()
    for competitor in competitors:
        normalized = competitor.name.strip().lower()
        if not normalized or normalized in seen_names or _looks_same_brand(brand.name, competitor.name):
            db.delete(competitor)
            continue
        seen_names.add(normalized)


def merge_duplicate_brands(db: Session, org_id: int) -> bool:
    from app.models import Brand, Competitor, Prompt, Report, Run

    brands = list(
        db.scalars(select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc()))
    )
    if len(brands) <= 1:
        return False

    changed = False
    primary_by_token: dict[str, Brand] = {}
    for brand in brands:
        tokens = brand_identity_tokens(brand.name, brand.aliases)
        primary = next((primary_by_token[token] for token in tokens if token in primary_by_token), None)
        if not primary:
            for token in tokens:
                primary_by_token[token] = brand
            continue
        if primary.id == brand.id:
            continue

        merged_aliases = normalize_brand_aliases(
            primary.name,
            [*(primary.aliases or []), brand.name, *(brand.aliases or [])],
        )
        if primary.aliases != merged_aliases:
            primary.aliases = merged_aliases
            changed = True

        inferred_context = infer_project_context(primary.name, primary.project_context, merged_aliases)
        if inferred_context == "通用行业":
            inferred_context = infer_project_context(brand.name, brand.project_context, brand.aliases)
        if primary.project_context != inferred_context:
            primary.project_context = inferred_context
            changed = True

        existing_competitors = {
            item.name.lower()
            for item in db.scalars(
                select(Competitor).where(Competitor.org_id == org_id, Competitor.brand_id == primary.id)
            )
        }
        for competitor in db.scalars(
            select(Competitor).where(Competitor.org_id == org_id, Competitor.brand_id == brand.id)
        ):
            if competitor.name.lower() in existing_competitors or _looks_same_brand(primary.name, competitor.name):
                db.delete(competitor)
                changed = True
                continue
            competitor.brand_id = primary.id
            existing_competitors.add(competitor.name.lower())
            changed = True

        for prompt in db.scalars(
            select(Prompt).where(Prompt.org_id == org_id, Prompt.brand_id == brand.id)
        ):
            prompt.brand_id = primary.id
            changed = True
        for run in db.scalars(select(Run).where(Run.org_id == org_id, Run.brand_id == brand.id)):
            run.brand_id = primary.id
            changed = True
        for report in db.scalars(
            select(Report).where(Report.org_id == org_id, Report.brand_id == brand.id)
        ):
            report.brand_id = primary.id
            changed = True

        db.flush()
        db.execute(sa_delete(Brand).where(Brand.id == brand.id))
        changed = True

        for token in tokens:
            primary_by_token[token] = primary

    if changed:
        refreshed = list(
            db.scalars(select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc()))
        )
        for brand in refreshed:
            _dedupe_active_prompts(db, org_id, brand.id)
            _dedupe_competitors(db, org_id, brand)
    return changed


def find_existing_brand(
    db: Session,
    org_id: int,
    brand_name: str,
    aliases: Iterable[str] | None = None,
) -> "Brand | None":
    from app.models import Brand

    target_tokens = brand_identity_tokens(brand_name, aliases)
    if not target_tokens:
        return None
    brands = list(
        db.scalars(select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc()))
    )
    for brand in brands:
        if target_tokens & brand_identity_tokens(brand.name, brand.aliases):
            return brand
    return None


def refresh_brand_project_prompts(db: Session, org_id: int, brand: "Brand") -> None:
    _ensure_prompt_library(db, org_id, brand)


def ensure_brand_project_assets(
    db: Session,
    org_id: int,
    brand: "Brand",
    competitor_names: Iterable[str] | None = None,
) -> None:
    brand.project_context = normalize_project_context(brand.project_context)
    inferred_context = infer_project_context(brand.name, brand.project_context, brand.aliases)
    if brand.project_context != inferred_context:
        brand.project_context = inferred_context
    brand.aliases = normalize_brand_aliases(brand.name, brand.aliases)
    _dedupe_competitors(db, org_id, brand)
    db.flush()
    _replace_misaligned_competitors(db, org_id, brand)
    db.flush()
    replace_placeholder_competitors(db, org_id, brand)
    db.flush()
    _create_missing_competitors(db, org_id, brand, competitor_names=competitor_names)
    db.flush()
    _dedupe_competitors(db, org_id, brand)
    db.flush()
    _ensure_prompt_library(db, org_id, brand)
    db.flush()
    _dedupe_active_prompts(db, org_id, brand.id)
