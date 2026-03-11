from __future__ import annotations

ANALYSIS_MODULE_LAYERS = [
    {
        "level": "基础建设层",
        "goal": "试点验证与基础建设",
        "modules": [
            "AI品牌叙事体系设计",
            "产品卖点AI表达策略设计",
            "AI推荐场景设计与用户需求映射",
            "竞品AI可见度与推荐分析",
            "GEO品牌知识库建设",
            "AI内容矩阵规划与内容资产建设",
            "品牌露出策略优化",
        ],
    },
    {
        "level": "增长优化层",
        "goal": "增长优化与竞品对抗",
        "modules": [
            "AI搜索趋势与市场洞察研究",
            "行业AI提问场景库建设",
            "AI品牌叙事体系与定位策略设计",
            "AI产品策略与用户需求洞察",
            "AI舆情与负面语义监测",
            "GEO内容矩阵与品牌知识体系建设",
            "多AI平台GEO优化部署",
            "高层战略报告与品牌AI战略蓝图",
        ],
    },
    {
        "level": "战略治理层",
        "goal": "系统化布局与战略优化",
        "modules": [
            "品牌叙事一致性评估与纠偏机制",
            "跨平台推荐规则对冲策略",
            "风险预警清单与治理流程",
            "跨季度趋势评估与管理层决策摘要",
            "组织级AI品牌运营仪表盘",
        ],
    },
]

DELIVERY_STAGES = [
    {
        "stage": "试点验证与基础建设",
        "report_focus": "月度核心指标报告",
        "core_outputs": "提及率、推荐率、情感分布，验证基础监测与问题库有效性",
        "management_view": "季度复盘聚焦试点结果、能力短板与下一阶段资源配置建议",
    },
    {
        "stage": "增长优化与竞品对抗",
        "report_focus": "月度指标 + 对抗拆解",
        "core_outputs": "增加平台分布对比、竞品差距拆解、主题词表现分层、月度优化动作闭环追踪",
        "management_view": "季度复盘聚焦竞争态势、关键主题变化与策略成效评估",
    },
    {
        "stage": "系统化布局与战略优化",
        "report_focus": "月度运营 + 季度战略专题",
        "core_outputs": "增加季度策略专题、品牌叙事一致性评估、风险预警清单、跨季度趋势与管理层决策摘要",
        "management_view": "形成品牌AI战略蓝图与年度治理节奏",
    },
]


def get_analysis_framework() -> dict[str, object]:
    return {
        "module_layers": ANALYSIS_MODULE_LAYERS,
        "delivery_stages": DELIVERY_STAGES,
    }
