# Handoff Prompt — Vedic Divination Engine Build

将这个 prompt 交给下一个 agent 开始执行。

---

## 你的任务

在 `/Volumes/轻松打爆你/VIBE CODING/10_PROJECTS_ACTIVE/_playground/scratch/20260706-vedic-reading/` 目录下，搭建一个 **Vedic 占星计算引擎** 的 Python 项目骨架，然后按 6 个 Phase 执行。规划文档已经写好在 `tasks/` 目录，你做 build。

## 必须先读的文件（开工前）

按顺序读：
1. `tasks/PRD.md` — 产品范围和验收标准
2. `tasks/ARCHITECTURE.md` — 技术架构和数据流
3. `tasks/DATA-SCHEMA.md` — 输出 JSON 格式规范
4. `tasks/TASK-PLAN.md` — 6 阶段任务拆解（含工时、文件清单、验收标准）
5. `RULES.md` — LLM 解盘时的反污染规则（Phase 5 才用，但先知道）
6. `vedic-profile.md` — 现有参考数据，1995-07-21 的真实星盘，用作测试黄金标准

## 项目位置

在 scratch 目录下创建 `vedic-engine/`：

```
/Volumes/轻松打爆你/VIBE CODING/10_PROJECTS_ACTIVE/_playground/scratch/20260706-vedic-reading/vedic-engine/
```

不要创建新的 project folder，这是 playground scratch experiment。

## 已确定的决策（不要推翻）

- **岁差**: Lahiri（固定，用 `swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)`）
- **黄道制**: 恒星黄道 (Sidereal)
- **交点算法**: 真交点 (True Node)
- **行星位置**: 视位置 (Apparent)
- **宫位系统**: Placidus（默认）
- **大运**: Vimshottari，365.25 天/年，Moon 起点
- **计算引擎**: `pyswisseph` (v2.10.3.2) + `PyJHora`（高级 Vedic 逻辑）
- **后端框架**: FastAPI
- **LLM**: Claude API（OpenAI 兼容接口也可切换）
- **图式默认**: South Indian

## 执行顺序

严格按 TASK-PLAN.md 的 Phase 顺序走：
P0 → P1 → P2 → P3+P4 并行 → P5 → P6

每个 Phase 做完后汇报：完成了什么文件，验收标准通过情况。

## 关键参考资源

- maitreya8 源码（已分析过，不需要重新 clone，除非需要看公式细节）：
  - Yoga 规则: `src/jyotish/Yoga.cpp`
  - Dasha 算法: `src/jyotish/VimsottariDasa.cpp`
  - 图式布局: `src/gui/VedicRasiChart.cpp`（三种 setupSouth/setupNorth/setupEast）
  - 岁差映射: `src/swe/swephexp.h`（SE_SIDM 常量定义）
  - GitHub: https://github.com/martin-pe/maitreya8

- Swiss Ephemeris 星历文件需从 AstroDienst 下载到 `ephe/` 目录
  - 下载地址: https://www.astro.com/ftp/swisseph/ephe/
  - 最少需要: `sepl_18.se1`, `semo_18.se1`, `seas_18.se1`

## 测试数据

用这个数据做所有测试和验证：

```
出生日期: 1995-07-21
出生时间: 11:35:00
时区: Asia/Taipei (UTC+08:00)
纬度: 25.037800
经度: 121.565000
```

预期关键值（Lahiri 岁差 = 23.797701°）：
- Sun: 巨蟹座(4), 第11宫, 4°8'
- Moon: 白羊座(1), 第8宫, 22°56', 胃宿Pada3
- Asc: 处女座(6), 第1宫, 27°39', 角宿Pada2
- Rahu: 天秤座(7), 第2宫, 7°48'（逆行）
- Rahu-Rahu 大运始于 2024.02
- SAV 第5宫 = 23（全盘最低并列）

Phase 2 必须对账，差异超过 0°01' 要排查。

## 输出格式

- 计算输出 JSON 必须匹配 DATA-SCHEMA.md 的结构
- LLM 解盘输出 Markdown，遵守 RULES.md 全部约束
- 图表输出 SVG

## 安全边界

- 可自由创建文件、安装 pip 包、运行本地服务
- 不要 git push
- 不要写入 ~/.claude/ 或系统配置
- 不要修改 scratch/20260706-vedic-reading/ 下的已有文件（vedic-profile.md, RULES.md, investment-advice.md, relationship-analysis.md, tasks/*）
- .env 文件放 API key 时确保在 .gitignore

## 遇到阻塞时

1. 先查 pyswisseph 官方文档
2. 再看 maitreya8 源码对应模块
3. 仍然不行 → 记录具体问题 + 已尝试的方案，交给下一个 agent 继续

开始执行。
