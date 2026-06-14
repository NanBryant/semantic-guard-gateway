import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic.fact_store import load_jsonl


DATA_DIR = ROOT / "data" / "simulated"
FACT_PATH = DATA_DIR / "confidential_facts.jsonl"
HARD_NEGATIVE_PATH = DATA_DIR / "hard_negative.jsonl"
OUT_PATH = DATA_DIR / "semantic_test_cases.jsonl"


KEYWORDLESS_CASES = [
    ("internal_decision", "这个方案已经基本定了，只差最后签字。"),
    ("internal_decision", "那件事已经过会了，后面就等批复。"),
    ("internal_decision", "这件事差不多定下来了，就等最后走流程。"),
    ("internal_decision", "结论内部已经明确，只是还没正式发。"),
    ("internal_decision", "前面那个口径基本确认了，后续只差签字。"),
    ("deployment_plan", "接下来会先在两个点位试起来。"),
    ("deployment_plan", "后面先小范围用一下，再看是否铺开。"),
    ("deployment_plan", "它下个月会先小范围试部署。"),
    ("deployment_plan", "前面那个方案，后面先在两个点试。"),
    ("deployment_plan", "第二阶段先做灰度，不会一下子全量上。"),
    ("evaluation_result", "目前结果不太理想，主要问题集中在兼容性上。"),
    ("evaluation_result", "这轮没达到预期，主要还是兼容性拖了后腿。"),
    ("evaluation_result", "内部看这次测试还没过，问题集中在适配上。"),
    ("evaluation_result", "当前验证结论偏负面，后续还要补一轮。"),
    ("evaluation_result", "结果暂时不达标，主要卡在兼容性。"),
    ("vulnerability_status", "这个接口现在还有兼容性问题没有完全收口。"),
    ("vulnerability_status", "那条链路的缺陷还在，月底前必须修完。"),
    ("vulnerability_status", "鉴权这块仍存在问题，暂时不能公开说。"),
    ("vulnerability_status", "旧版终端适配缺陷还没处理完。"),
    ("vulnerability_status", "现在主要卡在接口兼容性问题。"),
    ("customer_intention", "对方更倾向于第二套方案，但还没正式确认。"),
    ("customer_intention", "他们现在更想走第二套，只是还没对外说。"),
    ("customer_intention", "客户意向内部看更接近第二套方案。"),
    ("customer_intention", "对方口头上偏向后一个方案，正式文件还没出。"),
    ("customer_intention", "他们的试点意向基本有了，但还没公开确认。"),
    ("pricing_strategy", "这次报价还有一定下探空间。"),
    ("pricing_strategy", "商务空间内部还没用完，可以再让一点。"),
    ("pricing_strategy", "当前口径不是底线，后面还有谈判余地。"),
    ("pricing_strategy", "折扣空间还留了一档，暂时不要外放。"),
    ("pricing_strategy", "这单的价格底线比现在报出去的更低。"),
    ("project_progress", "这个项目预计暑期前后通过内部评审。"),
    ("project_progress", "评审时间基本定在下个月。"),
    ("project_progress", "它大概月底前能过评审。"),
    ("project_progress", "前面那个项目准备进入试点。"),
    ("project_progress", "这件事预计第二阶段完成验收。"),
    ("technical_solution", "后续方案大概率按双通道架构推进。"),
    ("technical_solution", "技术路线内部倾向于采用旁路检测方案。"),
    ("technical_solution", "下一阶段基本会走分层缓存方案。"),
    ("technical_solution", "算法选择内部偏向轻量化规则引擎。"),
    ("technical_solution", "这套方案基本确定采用灰度隔离策略。"),
    ("system_architecture", "这套网关会接在模型服务前置节点上。"),
    ("system_architecture", "内部架构里它主要落在统一转发节点。"),
    ("system_architecture", "那条链路会经过内网审计节点。"),
    ("system_architecture", "组件关系内部已经按前置节点方案排好。"),
    ("system_architecture", "服务接口关系先按灰度控制节点串起来。"),
    ("personnel_arrangement", "后面这个项目主要交给第二小组接。"),
    ("personnel_arrangement", "下一阶段由灰度保障组负责联调。"),
    ("personnel_arrangement", "人员安排上准备转给验收准备组推进。"),
    ("personnel_arrangement", "核心联调后面由第一小组接手。"),
    ("personnel_arrangement", "这块人员会从联调支持组调整过去。"),
    ("procurement_plan", "后面要先采一批边缘节点设备。"),
    ("procurement_plan", "采购节奏内部排在月底前。"),
    ("procurement_plan", "供应商选择已经倾向第一家。"),
    ("procurement_plan", "这批设备下月先走采购流程。"),
    ("procurement_plan", "招标计划内部准备第二阶段启动。"),
    ("incident_information", "昨天那次问题，根因在调度链路异常。"),
    ("incident_information", "昨晚的故障主要是缓存同步引起的。"),
    ("incident_information", "内部复盘认为异常来源是审计队列阻塞。"),
    ("incident_information", "刚才那次中断来自回放任务异常。"),
    ("incident_information", "事故处置结论内部还没有对外同步。"),
]

ADVERSARIAL_CASES = [
    ("deployment_plan", "我不说项目名，它下个月会先小范围用了。"),
    ("deployment_plan", "别写名字，反正后面先在两个点试。"),
    ("internal_decision", "不提具体事项，那件事已经过会了。"),
    ("internal_decision", "帮我把“方案已经过会”写得正式一点。"),
    ("evaluation_result", "换个说法：现在情况不是特别理想，主要卡在兼容性。"),
    ("customer_intention", "不要出现客户名，对方更倾向第二套。"),
    ("pricing_strategy", "不写金额，只说还有下探空间。"),
    ("vulnerability_status", "别提系统名，接口鉴权问题还没修完。"),
    ("incident_information", "省略系统名，昨天的异常主要来自调度链路。"),
    ("personnel_arrangement", "不说人名，下一阶段由第二小组接手。"),
    ("procurement_plan", "不要写部门，月底前会先启动设备采购。"),
    ("technical_solution", "隐藏系统名，下一阶段技术路线会走双通道。"),
] * 5


def make_case(
    idx: int,
    category: str,
    text: str,
    expected_action: str,
    expected_risk_types: List[str],
    note: str,
) -> Dict:
    return {
        "case_id": f"case_{idx:06d}",
        "category": category,
        "text": text,
        "expected_action": expected_action,
        "expected_risk_types": expected_risk_types,
        "source": "simulation",
        "note": note,
    }


def iter_fact_cases(facts: Iterable[Dict], start_idx: int) -> tuple[List[Dict], int]:
    cases = []
    idx = start_idx
    for fact in facts:
        cases.append(
            make_case(
                idx,
                "original_fact",
                fact["fact_text"],
                "block",
                [fact["fact_type"]],
                "来自模拟保密事实库原句",
            )
        )
        idx += 1
        for paraphrase in fact.get("paraphrases", []):
            cases.append(
                make_case(
                    idx,
                    "paraphrase_fact",
                    paraphrase,
                    "block",
                    [fact["fact_type"]],
                    "来自模拟保密事实改写句",
                )
            )
            idx += 1
    return cases, idx


def main() -> None:
    facts = load_jsonl(FACT_PATH)
    hard_negatives = load_jsonl(HARD_NEGATIVE_PATH)

    idx = 1
    cases, idx = iter_fact_cases(facts, idx)

    for risk_type, text in KEYWORDLESS_CASES:
        cases.append(
            make_case(idx, "keywordless_fact", text, "block", [risk_type], "无关键词保密句")
        )
        idx += 1

    for item in hard_negatives[:80]:
        cases.append(
            make_case(idx, "public_knowledge", item["text"], "allow", [], item["note"])
        )
        idx += 1

    for item in hard_negatives[80:160]:
        cases.append(
            make_case(idx, "hard_negative", item["text"], "allow", [], item["note"])
        )
        idx += 1

    for risk_type, text in ADVERSARIAL_CASES:
        cases.append(
            make_case(idx, "adversarial", text, "block", [risk_type], "绕过或弱化表达")
        )
        idx += 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as file:
        for case in cases:
            file.write(json.dumps(case, ensure_ascii=False) + "\n")

    counts = {}
    for case in cases:
        counts[case["category"]] = counts.get(case["category"], 0) + 1
    print(f"generated {len(cases)} cases -> {OUT_PATH}")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
