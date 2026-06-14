ALLOWED_FACT_TYPES = {
    "project_progress": "未公开的立项、评审、试点、上线、验收进度",
    "technical_solution": "未公开的技术路线、算法选择、架构方案",
    "system_architecture": "内部网络、组件、服务、接口关系",
    "vulnerability_status": "系统缺陷、未修复漏洞、兼容性问题",
    "customer_intention": "客户未公开采购、合作、试点意向",
    "pricing_strategy": "底价、折扣、商务策略、谈判空间",
    "internal_decision": "内部结论、审批状态、领导意见",
    "personnel_arrangement": "内部岗位调整、项目成员安排",
    "procurement_plan": "未公开采购、招标、供应商选择",
    "deployment_plan": "未公开上线、迁移、扩容、内网部署计划",
    "evaluation_result": "测试、压测、评测、验收结论",
    "incident_information": "内部故障、事故、应急处置情况",
}


def is_allowed_fact_type(value: str) -> bool:
    return value in ALLOWED_FACT_TYPES
