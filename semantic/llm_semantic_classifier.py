import json
import re
from typing import Dict, List, Tuple


PUBLIC_PATTERNS = [
    r"请解释",
    r"什么是",
    r"一般",
    r"通常",
    r"如何",
    r"怎么",
    r"哪些",
    r"模板",
    r"虚构",
    r"假设",
    r"举一个",
    r"示例",
    r"科普",
    r"概念",
    r"流程",
    r"应该怎么写",
]

DISCLOSURE_MARKERS = [
    r"已经",
    r"基本定",
    r"只差",
    r"通过内部评审",
    r"过会",
    r"下个月",
    r"接下来",
    r"先在",
    r"小范围",
    r"倾向",
    r"还没.*确认",
    r"不理想",
    r"底价",
    r"下探",
    r"昨",
    r"异常",
    r"故障",
]

RISK_PATTERNS: Dict[str, List[Tuple[str, float, str]]] = {
    "internal_decision": [
        (r"基本定了", 0.9, "表达内部决策状态"),
        (r"差不多定下", 0.88, "表达内部决策状态"),
        (r"只差.*签字", 0.9, "表达审批签字状态"),
        (r"最后.*流程", 0.84, "表达内部审批流程"),
        (r"已经过会", 0.88, "表达未公开会议结论"),
        (r"等批复", 0.84, "表达内部批复状态"),
        (r"结论.*(明确|确认)", 0.84, "表达内部结论状态"),
        (r"内部结论", 0.86, "表达内部结论"),
    ],
    "deployment_plan": [
        (r"接下来.*(点位|试部署|试起来|试点)", 0.88, "表达未公开部署计划"),
        (r"下个?月.*(试|小范围|灰度|部署|上线)", 0.88, "表达未公开部署时间"),
        (r"先在.*(点位|两个点|小范围).*试", 0.88, "表达试点部署范围"),
        (r"小范围.*(用|试|部署|灰度)", 0.84, "表达小范围部署安排"),
        (r"先做灰度", 0.84, "表达灰度部署安排"),
        (r"不会.*全量上", 0.82, "表达未公开发布节奏"),
        (r"计划.*(迁移|扩容|内网部署|试部署)", 0.82, "表达部署安排"),
    ],
    "evaluation_result": [
        (r"结果.*不.*理想", 0.88, "表达内部评估结果"),
        (r"没达到预期", 0.86, "表达内部评估结果"),
        (r"还没过", 0.84, "表达内部测试结论"),
        (r"验证结论.*负面", 0.84, "表达内部验证结论"),
        (r"不达标", 0.84, "表达内部评估结论"),
        (r"压测.*(不理想|没有达到预期|没达到预期)", 0.88, "表达内部压测结论"),
        (r"验收.*(没过|未通过|不通过)", 0.86, "表达内部验收结论"),
        (r"问题集中在.*兼容性", 0.86, "表达内部测试问题"),
    ],
    "vulnerability_status": [
        (r"仍存在.*(漏洞|缺陷|兼容性问题|问题)", 0.88, "表达未修复问题"),
        (r"(接口|鉴权|链路).*(兼容性|缺陷|漏洞|问题)", 0.86, "表达系统缺陷状态"),
        (r"主要.*(卡在|集中在).*兼容性", 0.84, "表达兼容性缺陷"),
    ],
    "customer_intention": [
        (r"(客户|对方).*(倾向|更想|更偏向).*(方案|合作|采购|试点)", 0.88, "表达客户未公开意向"),
        (r"(客户|对方).*(倾向|更想|更偏向).*第二套", 0.88, "表达客户未公开意向"),
        (r"口头上偏向.*方案", 0.84, "表达客户未公开倾向"),
        (r"试点意向.*(没公开|公开确认|正式)", 0.84, "表达客户未公开试点意向"),
        (r"还没正式确认", 0.8, "表达未公开确认状态"),
    ],
    "pricing_strategy": [
        (r"(报价|底价|折扣).*(下探|空间|谈判|让步)", 0.9, "表达报价策略"),
        (r"下探空间", 0.86, "表达报价策略"),
        (r"谈判余地", 0.84, "表达商务谈判空间"),
        (r"价格底线", 0.86, "表达价格底线"),
        (r"商务.*(策略|空间|底线)", 0.86, "表达商务策略"),
    ],
    "project_progress": [
        (r"预计.*(完成|通过).*内部评审", 0.88, "表达项目评审进度"),
        (r"(完成|通过).*内部评审", 0.86, "表达内部评审状态"),
        (r"(过评审|能过评审|通过评审)", 0.82, "表达评审状态"),
        (r"准备进入试点", 0.86, "表达项目试点进展"),
        (r"评审时间.*(定在|基本定)", 0.84, "表达未公开评审时间"),
        (r"预计.*完成验收", 0.84, "表达验收进度"),
    ],
    "technical_solution": [
        (r"计划采用.*(方案|算法|技术路线|架构)", 0.84, "表达技术路线选择"),
        (r"基本确定采用.*方案", 0.86, "表达方案选择结果"),
        (r"下一阶段技术路线", 0.82, "表达技术路线"),
    ],
    "system_architecture": [
        (r"部署在.*(节点|内网|前置)", 0.86, "表达内部部署位置"),
        (r"(组件|服务|接口).*关系", 0.82, "表达系统内部架构"),
        (r"内网.*(节点|链路|网段)", 0.86, "表达内部网络结构"),
    ],
    "personnel_arrangement": [
        (r"(小组|团队|人员).*(接手|调整|转入|负责)", 0.86, "表达人员安排"),
        (r"下阶段由.*接手", 0.88, "表达项目交接安排"),
    ],
    "procurement_plan": [
        (r"(下月|月底|计划).*(采购|招标|供应商)", 0.88, "表达采购计划"),
        (r"供应商.*(定了|倾向|入围)", 0.86, "表达供应商选择"),
    ],
    "incident_information": [
        (r"(昨天|昨晚|刚才).*(异常|故障|事故)", 0.88, "表达内部事件信息"),
        (r"异常.*(来自|集中在|原因)", 0.86, "表达故障原因"),
        (r"应急处置", 0.84, "表达应急处置信息"),
    ],
}


def build_prompt(sentence: str) -> str:
    return f"""你是一个保密信息识别器。请判断下面句子是否表达了单位内部未公开事实。
只输出 JSON。
句子：{sentence}
"""


class RuleBasedSemanticClassifier:
    def classify(self, sentence: str) -> Dict:
        text = (sentence or "").strip()
        if not text:
            return self._allow("空句子")

        public_hit = self._has_any(text, PUBLIC_PATTERNS)
        disclosure_hit = self._has_any(text, DISCLOSURE_MARKERS)
        if public_hit and not disclosure_hit:
            return {
                "is_confidential_sentence": False,
                "risk_score": 0.12,
                "risk_types": [],
                "reason": "公开知识、模板或假设类请求",
                "is_public_knowledge": True,
            }

        matches = []
        for risk_type, patterns in RISK_PATTERNS.items():
            for pattern, score, reason in patterns:
                if re.search(pattern, text):
                    matches.append((risk_type, score, reason))
                    break

        if not matches:
            return self._allow("未发现内部未公开事实表达")

        risk_types = sorted({item[0] for item in matches})
        score = min(0.98, max(item[1] for item in matches) + 0.03 * (len(risk_types) - 1))
        reasons = "；".join(item[2] for item in matches[:2])
        return {
            "is_confidential_sentence": score >= 0.75,
            "risk_score": round(score, 4),
            "risk_types": risk_types,
            "reason": reasons,
            "is_public_knowledge": False,
        }

    @staticmethod
    def _has_any(text: str, patterns: List[str]) -> bool:
        return any(re.search(pattern, text) for pattern in patterns)

    @staticmethod
    def _allow(reason: str) -> Dict:
        return {
            "is_confidential_sentence": False,
            "risk_score": 0.08,
            "risk_types": [],
            "reason": reason,
            "is_public_knowledge": False,
        }


class LLMSemanticClassifier:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.local_classifier = RuleBasedSemanticClassifier()

    def classify(self, sentence: str) -> Dict:
        if self.llm_client is None:
            return self.local_classifier.classify(sentence)

        raw = self.llm_client.complete(build_prompt(sentence))
        try:
            data = json.loads(raw)
        except Exception:
            return {
                "is_confidential_sentence": True,
                "risk_score": 0.75,
                "risk_types": ["classifier_parse_error"],
                "reason": "分类器输出解析失败，按保守策略处理",
                "is_public_knowledge": False,
            }
        return data
