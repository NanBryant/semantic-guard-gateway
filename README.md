# 电子围栏：句级语义拦截网关

这是把 1-4 号任务合并后的完整演示项目，核心目标是识别“整句话本身表达内部未公开事实”的风险，并在高风险时拦截整段请求，避免将原文发送给模型。

## 项目结构

- `app.py`：FastAPI HTTP 入口，提供 `POST /chat`。
- `core/`：句子切分、规则检测、网关调度、统一返回结构。
- `semantic/`：模拟事实库读取、相似度匹配、语义分类、融合检测接口。
- `policy/`：严格模式决策与安全审计日志。
- `llm/`：演示用 LLM mock 客户端，被拦截时不会调用。
- `data/simulated/`：全部模拟事实库、hard negative、语义测试集。
- `scripts/`：数据生成、校验、评估、演示脚本。
- `tests/`：核心行为测试。

## 快速开始

```powershell
cd C:\Users\27167\Desktop\电子围栏
python -m pip install -r requirements.txt
python scripts\generate_simulated_facts.py
python scripts\validate_fact_schema.py
python scripts\build_semantic_test_cases.py
pytest
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Windows PowerShell 下也可以使用更稳的后台启动脚本：

```powershell
.\start_server.ps1
```

停止服务：

```powershell
.\stop_server.ps1
```

启动后测试：

```powershell
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u1\",\"text\":\"请帮我润色：这个方案已经基本定了，只差最后签字。\"}"
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u1\",\"text\":\"请解释什么是项目评审。\"}"
```

## 评估

```powershell
python scripts\evaluate_semantic_guard.py --direct
```

输出包含整体准确率、无关键词召回率、改写召回率、误报率、绕过表达召回率和 p95 延迟。错误样本会写入 `reports/semantic_errors.json`。

## 安全约束

- 本项目所有事实、客户、项目、系统、人员、时间和结论均为虚构模拟数据。
- 高风险请求默认整段拦截，不做局部替换，不调用 LLM。
- 审计日志默认写入 `reports/audit_semantic.log`，只保存句子 hash、风险类型、分数和动作，不保存高风险原文。
