from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from core.guard_orchestrator import handle_chat


app = FastAPI(title="电子围栏句级语义拦截网关", version="2.0.0")


class ChatRequest(BaseModel):
    text: str = Field(default="", description="用户输入文本")
    user_id: str = Field(default="demo_user", description="演示用户 ID")
    request_id: Optional[str] = Field(default=None, description="可选请求 ID")
    mode: str = Field(default="strict", description="strict / sentence_only / allow")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>电子围栏语义拦截网关</title>
  <style>
    :root {
      color-scheme: light;
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      background: #f5f7fb;
      color: #162033;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }
    header {
      background: #16324f;
      color: white;
      padding: 18px 28px;
      border-bottom: 4px solid #2a9d8f;
    }
    header h1 {
      margin: 0;
      font-size: 22px;
      font-weight: 650;
      letter-spacing: 0;
    }
    main {
      width: min(980px, calc(100vw - 32px));
      margin: 28px auto;
      display: grid;
      gap: 16px;
    }
    .panel {
      background: #ffffff;
      border: 1px solid #d9e2ec;
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 24px rgba(22, 32, 51, 0.08);
    }
    label {
      display: block;
      font-size: 14px;
      font-weight: 650;
      margin-bottom: 8px;
    }
    textarea {
      width: 100%;
      min-height: 132px;
      resize: vertical;
      border: 1px solid #b7c4d3;
      border-radius: 6px;
      padding: 12px;
      font: inherit;
      line-height: 1.55;
    }
    .actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }
    button {
      border: 0;
      border-radius: 6px;
      background: #1b6ca8;
      color: white;
      padding: 10px 16px;
      font: inherit;
      font-weight: 650;
      cursor: pointer;
    }
    button.secondary { background: #52616f; }
    button:disabled { opacity: .65; cursor: wait; }
    .status {
      font-size: 14px;
      color: #52616f;
    }
    .result-head {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border-radius: 999px;
      padding: 4px 10px;
      font-weight: 700;
      font-size: 13px;
      background: #e8edf3;
      color: #243447;
    }
    .badge.block { background: #ffe8e3; color: #a13a25; }
    .badge.allow { background: #e3f6ef; color: #17694f; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #111827;
      color: #e5edf7;
      border-radius: 6px;
      padding: 14px;
      overflow: auto;
      max-height: 460px;
      line-height: 1.5;
    }
    .samples {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 8px;
    }
    .sample {
      text-align: left;
      background: #edf2f7;
      color: #1f2d3d;
      border: 1px solid #d3dde8;
      font-weight: 500;
    }
  </style>
</head>
<body>
  <header>
    <h1>电子围栏语义拦截网关</h1>
  </header>
  <main>
    <section class="panel">
      <label for="text">输入待检测文本</label>
      <textarea id="text">请帮我润色：这个方案已经基本定了，只差最后签字。</textarea>
      <div class="actions">
        <button id="submit">检测</button>
        <button class="secondary" id="clear">清空</button>
        <span class="status" id="status">服务已就绪</span>
      </div>
    </section>
    <section class="panel">
      <label>示例</label>
      <div class="samples">
        <button class="sample" data-text="请帮我润色：这个方案已经基本定了，只差最后签字。">无关键词保密句</button>
        <button class="sample" data-text="接下来会先在两个点位试起来。">部署计划</button>
        <button class="sample" data-text="请解释什么是项目评审。">公开知识</button>
        <button class="sample" data-text="请写一个虚构的项目进度汇报模板。">虚构模板</button>
      </div>
    </section>
    <section class="panel">
      <div class="result-head">
        <span class="badge" id="actionBadge">等待检测</span>
        <span class="status" id="score"></span>
      </div>
      <pre id="result">点击“检测”后显示结果。</pre>
    </section>
  </main>
  <script>
    const text = document.querySelector("#text");
    const submit = document.querySelector("#submit");
    const clear = document.querySelector("#clear");
    const statusEl = document.querySelector("#status");
    const result = document.querySelector("#result");
    const actionBadge = document.querySelector("#actionBadge");
    const score = document.querySelector("#score");

    function render(data) {
      const action = data.action || "unknown";
      actionBadge.textContent = action === "block" ? "已拦截" : action === "allow" ? "已放行" : action;
      actionBadge.className = "badge " + action;
      score.textContent = typeof data.risk_score === "number" ? "risk_score: " + data.risk_score : "";
      result.textContent = JSON.stringify(data, null, 2);
    }

    async function detect() {
      submit.disabled = true;
      statusEl.textContent = "检测中";
      try {
        const resp = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: "web_demo", text: text.value })
        });
        const data = await resp.json();
        render(data);
        statusEl.textContent = "检测完成";
      } catch (err) {
        actionBadge.textContent = "请求失败";
        actionBadge.className = "badge block";
        result.textContent = String(err);
        statusEl.textContent = "服务未响应";
      } finally {
        submit.disabled = false;
      }
    }

    submit.addEventListener("click", detect);
    clear.addEventListener("click", () => { text.value = ""; text.focus(); });
    document.querySelectorAll(".sample").forEach((btn) => {
      btn.addEventListener("click", () => { text.value = btn.dataset.text; detect(); });
    });
  </script>
</body>
</html>
"""


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    return handle_chat(request.model_dump())
