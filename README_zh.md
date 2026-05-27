# IEEE Paper Radar

每周自动从 IEEE Xplore 抓取最新论文，通过 AI 按个人研究方向排序，将精选摘要发送到你的邮箱。

[English](README.md) | [한국어](README_ko.md)

## 功能流程

1. **抓取** IEEE Xplore 指定期刊/会议的最新论文（TPEL、TIE、ECCE、APEC）
2. **补充** 从 Semantic Scholar 获取每篇论文的引用数
3. **摘要** 用 Gemini AI 为每篇论文生成 2–3 句贡献描述
4. **推荐** 对照你的研究档案进行三档排序（强烈推荐 / 值得一读 / 跳过）
5. **趋势** 分析过去两年文献的研究方向演变
6. **发送** 格式化 HTML 邮件到你的收件箱

## 快速上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置研究方向

编辑 `config.py` 顶部的 **用户设置** 区域：

```python
# 收件人
RECIPIENT_EMAILS = ["你的邮箱@gmail.com"]

# 搜索词：论文必须包含所有必选词，且至少包含一个上下文词
KEYWORDS_REQUIRED = ["switched capacitor"]
KEYWORDS_CONTEXT  = ["data center", "48V bus", "rack power", "server rack"]

# 监控的 IEEE 期刊/会议
VENUES = {
    "TPEL": "IEEE Transactions on Power Electronics",
    ...
}

# 你的研究档案——AI 用它来判断论文与你研究的相关性
RESEARCH_PROFILE = """
研究方向：...
重点关注：...
"""
```

### 3. 填写密钥

将 `.env.example` 复制为 `.env` 并填写：

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=AIza...          # aistudio.google.com/apikey（免费）
IEEE_XPLORE_API_KEY=...         # developer.ieee.org（免费）
SENDER_EMAIL=你的账号@gmail.com
SENDER_PASSWORD=xxxx-xxxx-xxxx  # Gmail 应用专用密码，不是账号密码
```

> **Gmail 应用专用密码**：前往 [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 生成。

## 使用方法

```bash
# 仅首次运行：初始化过去两年历史数据（不发邮件）
python main.py --init

# 每周运行：抓取 → 补充 → 摘要 → 推荐 → 发邮件
python main.py
```

### Windows 定时任务

项目包含 `run_weekly.bat`，可配合 Windows 任务计划程序实现每周自动运行。

## 邮件格式

```
[IEEE Paper Radar] 2026-W22 | 5 篇新论文

📚 本周推荐
  ── 强烈推荐 ──────────────────────────
  ⭐⭐ A Soft-Switching Multiresonant...  (TPEL)
  理由：直接推进 RSCC 拓扑推导方法...

  ── 值得一读 ──────────────────────────
  ⭐ Flying Capacitor Multilevel...  (ECCE)

── 所有新论文（5 篇）─────────────────
  [1] ⭐⭐ 标题 — TPEL · 2026 · 引用数：3
      贡献：...

── 研究趋势分析 ──────────────────────
  演变叙述：...
  方向一：...
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 论文来源 | IEEE Xplore API |
| 引用数据 | Semantic Scholar API |
| AI 分析 | Google Gemini 2.5 Pro |
| 数据库 | SQLite |
| 邮件发送 | SMTP（Gmail） |
| 开发语言 | Python 3.12+ |

## 测试

```bash
python -m pytest tests/ -v
```

所有外部 API 均使用 mock，测试期间不会发起真实请求。
