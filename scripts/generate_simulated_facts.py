import json
import sys
from pathlib import Path
from typing import Callable, Dict, List


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic.fact_types import ALLOWED_FACT_TYPES


DATA_DIR = ROOT / "data" / "simulated"
FACT_PATH = DATA_DIR / "confidential_facts.jsonl"
HARD_NEGATIVE_PATH = DATA_DIR / "hard_negative.jsonl"
SCHEMA_PATH = DATA_DIR / "confidential_fact_schema.json"
TYPE_DOC_PATH = DATA_DIR / "fact_type_definition.md"

PROJECTS = ["天枢计划", "北辰工程", "星河平台", "青岚项目", "玄武网关", "云杉行动"]
SYSTEMS = ["云盾系统", "澜海平台", "智安网关", "磐石审计台", "灵犀调度器", "星桥网关"]
CUSTOMERS = ["星河集团", "北辰科技", "东岭单位", "华远研究院", "明川中心", "青石实验室"]
DEPARTMENTS = ["研发一部", "安全测试组", "平台运维组", "项目管理组", "交付保障组"]
TEAMS = ["第一小组", "第二小组", "灰度保障组", "联调支持组", "验收准备组"]
TIMES = ["下季度", "7月", "月底前", "暑期前后", "第二阶段", "下个月"]
SOLUTIONS = ["双通道审计架构", "灰度隔离策略", "分层缓存方案", "轻量化规则引擎", "旁路检测方案"]
PROBLEMS = ["接口鉴权兼容性问题", "批处理延迟问题", "旧版终端适配缺陷", "日志链路抖动问题"]
ITEMS = ["接口改造方案", "第二批试点范围", "验收材料口径", "灰度发布节奏", "联调问题清单"]
PROCURE_ITEMS = ["边缘节点设备", "审计采集组件", "测试终端套件", "日志存储模块", "备份网关"]
INCIDENTS = ["调度链路异常", "缓存同步故障", "边缘节点抖动", "审计队列阻塞", "回放任务中断"]


def pick(pool: List[str], idx: int, step: int = 1) -> str:
    return pool[(idx * step) % len(pool)]


def fact_record(
    idx: int,
    fact_type: str,
    fact_text: str,
    summary: str,
    paraphrases: List[str],
    negatives: List[str],
    keywords: List[str],
) -> Dict:
    return {
        "fact_id": f"fact_{idx:06d}",
        "fact_type": fact_type,
        "confidential_level": "high",
        "fact_text": fact_text,
        "fact_summary": summary,
        "paraphrases": paraphrases,
        "negative_samples": negatives,
        "keywords": keywords,
        "source": "simulation",
        "status": "active",
    }


def make_project_progress(idx: int) -> Dict:
    project, time = pick(PROJECTS, idx), pick(TIMES, idx, 2)
    return fact_record(
        idx,
        "project_progress",
        f"{project}预计{time}完成内部评审。",
        "某模拟内部项目存在未公开评审进度。",
        [
            f"{project}大概{time}能完成内部评审。",
            f"这个项目预计{time}前后通过内部评审。",
            f"{project}的评审时间基本定在{time}。",
        ],
        ["请解释什么是内部评审。", "项目评审一般包括哪些环节？"],
        [project, time, "内部评审"],
    )


def make_technical_solution(idx: int) -> Dict:
    system, solution = pick(SYSTEMS, idx), pick(SOLUTIONS, idx, 2)
    return fact_record(
        idx,
        "technical_solution",
        f"{system}计划采用{solution}作为下一阶段技术路线。",
        "某模拟系统存在未公开技术路线选择。",
        [
            f"{system}下一阶段基本会走{solution}。",
            f"技术路线内部倾向于采用{solution}。",
            f"后续方案大概率按{solution}推进。",
        ],
        ["技术路线评估通常看哪些指标？", "请举一个虚构的系统方案示例。"],
        [system, solution, "技术路线"],
    )


def make_system_architecture(idx: int) -> Dict:
    system = pick(SYSTEMS, idx, 2)
    node = pick(["模型服务前置节点", "内网审计节点", "统一转发节点", "灰度控制节点"], idx)
    return fact_record(
        idx,
        "system_architecture",
        f"{system}部署在{node}，负责统一流量控制。",
        "某模拟系统存在未公开内部部署结构。",
        [
            f"{system}的位置放在{node}前后。",
            f"内部架构里，{system}主要落在{node}。",
            f"这套网关会接在{node}上。",
        ],
        ["系统架构图一般包含哪些元素？", "请解释什么是前置节点。"],
        [system, node],
    )


def make_vulnerability_status(idx: int) -> Dict:
    system, problem, time = pick(SYSTEMS, idx), pick(PROBLEMS, idx), pick(TIMES, idx)
    return fact_record(
        idx,
        "vulnerability_status",
        f"{system}当前仍存在{problem}，需要在{time}前修复。",
        "某模拟系统存在未公开缺陷状态。",
        [
            f"{system}现在主要卡在{problem}。",
            f"{problem}还没有完全处理完。",
            f"内部确认{system}的{problem}要赶在{time}前收口。",
        ],
        ["软件缺陷通常如何分级？", "接口兼容性测试一般怎么做？"],
        [system, problem, time],
    )


def make_customer_intention(idx: int) -> Dict:
    customer = pick(CUSTOMERS, idx)
    return fact_record(
        idx,
        "customer_intention",
        f"{customer}倾向采用第二套方案，但尚未公开确认。",
        "某模拟客户存在未公开方案倾向。",
        [
            f"{customer}更偏向第二套方案，只是还没正式确认。",
            f"对方现在更想走第二套方案。",
            f"客户意向内部看更接近第二套方案。",
        ],
        ["客户意向分析通常包括哪些内容？", "请写一个虚构的客户访谈模板。"],
        [customer, "第二套方案"],
    )


def make_pricing_strategy(idx: int) -> Dict:
    customer, project = pick(CUSTOMERS, idx, 2), pick(PROJECTS, idx)
    return fact_record(
        idx,
        "pricing_strategy",
        f"{project}给{customer}的报价还有一定下探空间。",
        "某模拟项目存在未公开商务报价策略。",
        [
            f"{project}对{customer}这单还可以再让一点。",
            f"给{customer}的商务空间内部还没用完。",
            f"这次报价底线比当前口径更低。",
        ],
        ["报价策略课程通常讲什么？", "请写一个虚构的商务谈判场景。"],
        [customer, project, "报价"],
    )


def make_internal_decision(idx: int) -> Dict:
    item = pick(ITEMS, idx)
    return fact_record(
        idx,
        "internal_decision",
        f"{item}已经基本定了，只差最后签字。",
        "某模拟事项存在未公开内部决策状态。",
        [
            f"{item}差不多定下来了，就等最后走流程。",
            f"这件事内部已经过会，后面等批复。",
            f"{item}的结论基本明确，只剩签字确认。",
        ],
        ["请解释什么是内部审批。", "请写一个虚构的审批流程模板。"],
        [item, "签字"],
    )


def make_personnel_arrangement(idx: int) -> Dict:
    project, team = pick(PROJECTS, idx), pick(TEAMS, idx)
    return fact_record(
        idx,
        "personnel_arrangement",
        f"{project}下阶段由{team}接手核心联调工作。",
        "某模拟项目存在未公开人员安排。",
        [
            f"后面{project}主要交给{team}接。",
            f"{team}会在下一阶段负责{project}联调。",
            f"人员安排上，{project}准备转给{team}推进。",
        ],
        ["项目团队分工一般怎么写？", "请生成一个虚构的排班表示例。"],
        [project, team],
    )


def make_procurement_plan(idx: int) -> Dict:
    dept, item, time = pick(DEPARTMENTS, idx), pick(PROCURE_ITEMS, idx), pick(TIMES, idx)
    return fact_record(
        idx,
        "procurement_plan",
        f"{dept}计划{time}启动{item}采购。",
        "某模拟部门存在未公开采购安排。",
        [
            f"{dept}后面要先采一批{item}。",
            f"{item}采购节奏内部排在{time}。",
            f"采购计划里，{item}准备{time}先走流程。",
        ],
        ["采购流程一般有哪些步骤？", "请举一个虚构的供应商评分例子。"],
        [dept, item, time],
    )


def make_deployment_plan(idx: int) -> Dict:
    system, time = pick(SYSTEMS, idx), pick(TIMES, idx, 2)
    return fact_record(
        idx,
        "deployment_plan",
        f"{system}计划{time}先在两个点位试部署。",
        "某模拟系统存在未公开部署计划。",
        [
            f"{system}接下来会先在两个点位试起来。",
            f"这套系统{time}先小范围用一下。",
            f"部署节奏内部定为{time}做两个点位灰度。",
        ],
        ["灰度发布一般有哪些步骤？", "项目上线前一般要做哪些测试？"],
        [system, time, "试部署"],
    )


def make_evaluation_result(idx: int) -> Dict:
    system = pick(SYSTEMS, idx, 3)
    return fact_record(
        idx,
        "evaluation_result",
        f"{system}本轮压测结果不理想，主要问题集中在兼容性上。",
        "某模拟系统存在未公开评估结论。",
        [
            f"{system}这轮测试没达到预期，兼容性是主要问题。",
            f"目前结果不太理想，主要问题集中在兼容性上。",
            f"压测结论内部看还没过，兼容性拖了后腿。",
        ],
        ["系统兼容性测试一般怎么做？", "软件压测可以评估哪些能力？"],
        [system, "压测", "兼容性"],
    )


def make_incident_information(idx: int) -> Dict:
    system, incident = pick(SYSTEMS, idx), pick(INCIDENTS, idx)
    return fact_record(
        idx,
        "incident_information",
        f"{system}昨天的异常主要来自{incident}。",
        "某模拟系统存在未公开事件原因。",
        [
            f"昨天那次问题，根因在{incident}。",
            f"{system}昨晚的故障主要是{incident}引起的。",
            f"内部复盘认为异常来源是{incident}。",
        ],
        ["应急演练通常包含哪些环节？", "请解释什么是故障复盘。"],
        [system, incident],
    )


BUILDERS: List[Callable[[int], Dict]] = [
    make_project_progress,
    make_technical_solution,
    make_system_architecture,
    make_vulnerability_status,
    make_customer_intention,
    make_pricing_strategy,
    make_internal_decision,
    make_personnel_arrangement,
    make_procurement_plan,
    make_deployment_plan,
    make_evaluation_result,
    make_incident_information,
]


def build_facts(per_type: int = 18) -> List[Dict]:
    facts = []
    idx = 1
    for builder in BUILDERS:
        for _ in range(per_type):
            facts.append(builder(idx))
            idx += 1
    return facts


def build_hard_negatives(target_count: int = 240) -> List[Dict]:
    topics = [
        "内部评审",
        "项目试点",
        "系统压测",
        "客户意向分析",
        "报价策略",
        "采购流程",
        "应急演练",
        "技术路线评估",
        "部署计划",
        "人员排班",
        "接口兼容性测试",
        "验收流程",
        "项目进度汇报",
        "供应商选择",
        "灰度发布",
        "系统架构图",
    ]
    templates = [
        ("concept", "请解释什么是{topic}。"),
        ("general_process", "{topic}一般包括哪些环节？"),
        ("public_knowledge", "{topic}通常用于什么场景？"),
        ("writing_request", "请写一个虚构的{topic}模板。"),
        ("hypothetical", "假设某项目需要做{topic}，汇报材料应该怎么写？"),
        ("teaching_example", "请举一个{topic}的虚构例子。"),
        ("method", "{topic}有哪些常见方法？"),
        ("checklist", "帮我整理一份通用的{topic}检查清单。"),
    ]
    rows = []
    idx = 1
    while len(rows) < target_count:
        topic = topics[(idx - 1) % len(topics)]
        category, template = templates[((idx - 1) // len(topics)) % len(templates)]
        rows.append(
            {
                "negative_id": f"neg_{idx:06d}",
                "category": category,
                "text": template.format(topic=topic),
                "source": "simulation",
                "note": "看起来相关但不表达具体内部未公开事实",
            }
        )
        idx += 1
    return rows


def write_jsonl(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_schema() -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": [
            "fact_id",
            "fact_type",
            "confidential_level",
            "fact_text",
            "fact_summary",
            "paraphrases",
            "source",
            "status",
        ],
        "properties": {
            "fact_id": {"type": "string", "pattern": "^fact_[0-9]{6}$"},
            "fact_type": {"type": "string", "enum": sorted(ALLOWED_FACT_TYPES)},
            "confidential_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "fact_text": {"type": "string", "minLength": 1},
            "fact_summary": {"type": "string", "minLength": 1},
            "paraphrases": {"type": "array", "items": {"type": "string"}, "minItems": 2},
            "negative_samples": {"type": "array", "items": {"type": "string"}},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "source": {"const": "simulation"},
            "status": {"type": "string", "enum": ["active", "inactive"]},
        },
    }
    SCHEMA_PATH.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")


def write_fact_type_doc() -> None:
    lines = ["# 保密事实类型定义", ""]
    for code, desc in ALLOWED_FACT_TYPES.items():
        lines.append(f"- `{code}`：{desc}")
    TYPE_DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    facts = build_facts()
    hard_negatives = build_hard_negatives()
    write_jsonl(FACT_PATH, facts)
    write_jsonl(HARD_NEGATIVE_PATH, hard_negatives)
    write_schema()
    write_fact_type_doc()
    print(f"generated facts: {len(facts)} -> {FACT_PATH}")
    print(f"generated hard negatives: {len(hard_negatives)} -> {HARD_NEGATIVE_PATH}")
    print(f"wrote schema: {SCHEMA_PATH}")
    print(f"wrote type definition: {TYPE_DOC_PATH}")


if __name__ == "__main__":
    main()
