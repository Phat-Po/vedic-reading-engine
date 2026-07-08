# Vedic Reading Engine

[English README](README.md)

**自托管的吠陀占星引擎，提供 Swiss Ephemeris 排盘、SVG 星盘渲染、离线解读，以及 Codex / Claude skill 集成。**

这个仓库面向希望把 Jyotish 能力本地化、接口化的人：既可以当 CLI 用，也可以当 API 或 agent skill 用，而不是把核心排盘能力交给黑盒 SaaS。

---

## 快速开始

### 方式 1. Send This To Your AI Agent

把下面这段直接发给 Codex、Claude Code 或其他 coding agent：

```text
Clone this repository, read README.md first, then follow ONBOARDING_PROMPT.md. Install dependencies, run the primary smoke test, start the main entrypoint, and tell me exactly how to verify the project is working. Use the simplest supported setup path first. If setup fails, stop at the first concrete blocker and report it clearly.
```

直接复制的 prompt 文件：

- [ONBOARDING_PROMPT.md](ONBOARDING_PROMPT.md)

### 方式 2. 手动安装

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
vedic-calculate --sample
uvicorn vedic_engine.api:app --reload
```

然后打开：

```text
http://127.0.0.1:8000/docs
```

更完整的逐步安装说明见 [SETUP.md](SETUP.md)。

---

## 这个仓库提供什么

- 基于 Lahiri ayanamsa 的确定性吠陀排盘
- 南印度 / 北印度 / 东印度 / 大运 / Shadbala SVG 输出
- FastAPI 接口：calculate、chart、dasha、transit、interpret、full
- 遵守 [RULES.md](RULES.md) 的离线解读层
- 本地 CLI 入口和 skill 封装

---

## 文档导航

- [README.md](README.md)：英文主文档
- [ONBOARDING_PROMPT.md](ONBOARDING_PROMPT.md)：给 AI agent 的复制型安装 prompt
- [SETUP.md](SETUP.md)：安装与首次运行
- [docs/INDEX.md](docs/INDEX.md)：文档导航中心
- [CONTRIBUTING.md](CONTRIBUTING.md)：开发与本地边界
- [RULES.md](RULES.md)：防污染解读规则

---

## 说明

- 英文版 `README.md` 是主发布文档
- 本文件是中文入口，帮助快速理解和安装
- 更细的 API、模式、目录结构、故障排查等内容请看 [README.md](README.md)
