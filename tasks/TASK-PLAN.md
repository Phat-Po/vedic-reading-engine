# 任务拆解 — Vedic 卜卦系统

生成日期: 2026-07-06
状态: 规划完成，等待 `批准执行` 后开工

---

## 总览

| Phase | 名称 | 预估工时 | 依赖 | 可并行 |
|-------|------|---------|------|--------|
| P0 | 环境搭建 | 0.5h | — | — |
| P1 | 计算引擎 | 4-6h | P0 | — |
| P2 | 验证对标 | 1-2h | P1 | — |
| P3 | 图表渲染 | 3-4h | P1 | P4 可并行 |
| P4 | API 服务 | 2-3h | P1 | P3 可并行 |
| P5 | LLM 解盘 | 2-3h | P1+P2 | — |
| P6 | 整机测试 | 1-2h | P3+P4+P5 | — |

---

## Phase 0 — 环境搭建（0.5h）

### 0.1 创建 Python 项目骨架

**产出**：
```
vedic-engine/
├── pyproject.toml       # Python 项目配置
├── requirements.txt      # 依赖锁定
├── .env.example          # 环境变量模板
├── .gitignore
├── ephe/                 # Swiss Ephemeris 星历文件（需下载）
├── src/
│   ├── __init__.py
│   ├── calculator.py     # VedicCalculator 主类
│   ├── renderer.py       # ChartRenderer 图表渲染
│   ├── interpreter.py    # InterpretationEngine LLM 解盘
│   ├── schemas.py        # Pydantic 数据模型
│   ├── constants.py      # 星座/Nakshatra/Yoga 常量表
│   └── utils.py          # 角度转换/时间工具
├── tests/
│   ├── test_calculator.py
│   └── fixtures/
│       └── sample_birth_1995.json  # 1995-07-21 测试用例
├── templates/
│   ├── natal.md           # 本命盘 Prompt 模板
│   ├── investment.md      # 投资分析 Prompt
│   ├── relationship.md    # 感情分析 Prompt
│   └── rules.md           # RULES.md 副本（注入 Prompt）
└── tasks/                 # 规划文档 ← 当前目录
```

### 0.2 依赖安装

```
pyswisseph==2.10.3.2
pydantic>=3.0
fastapi>=0.115
uvicorn[standard]
httpx
matplotlib
svgwrite
python-dotenv
```

### 0.3 下载星历文件

从 AstroDienst 下载 Swiss Ephemeris 星历数据文件（`ephe/` 目录），约 40 MB：
- `sepl_18.se1`, `semo_18.se1`, `seas_18.se1`
- `fixstars.cat` (恒星目录)
- 放在 `vedic-engine/ephe/` 下

### 验收：
- [ ] `pip install -e .` 成功
- [ ] `pyswisseph` 可 import 且能找到星历文件
- [ ] `pytest` 框架就绪

---

## Phase 1 — 计算引擎（4-6h）

### 1.1 行星位置 + 宫位（1.5h）

**文件**: `src/calculator.py` (VedicCalculator 类)

实现：
- `_init_swe()` — 初始化 Swiss Ephemeris，设置 Lahiri 岁差
- `_calc_jd()` — 日期→儒略日转换
- `_calc_planets()` — 日月水金火土木天海冥 + 罗喉计都，返回视位置经度
- `_calc_houses()` — Placidus 宫位计算，返回 12 宫头
- `_calc_ascendant()` — 上升点 + MC
- `planet_to_sign_house()` — 行星经度 → 星座索引 + 宫位编号
- `planet_to_nakshatra()` — 行星经度 → Nakshatra + Pada + 宿主

**关键点**：
- 岁差用 `swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)` 固化
- 交点用 `swe.FLG_TRUE` 真交点
- 所有经度为 sidereal 值

### 1.2 Panchanga 五支历（0.5h）

**文件**: `src/calculator.py` (追加方法)

- `_calc_tithi()` — Sun-Moon 经度差 → Tithi
- `_calc_nakshatra()` — Moon 经度 → Nakshatra
- `_calc_yoga_panchanga()` — Sun+Moon 经度和 → Yoga
- `_calc_karana()` — Tithi 半期 → Karana
- `_calc_vara()` — 儒略日 → 星期

### 1.3 Upagraha 虚点（0.5h）

**文件**: `src/calculator.py` (追加方法)

参考 maitreya8 `VedicPlanet.cpp` 公式：
- Dhuma, Vyatipaata, Parivesha, Indrachaapa, Upaketu
- Kaala, Mrityu, Artha Praharaka, Yama Ghantaka
- Gulika, Maandi

### 1.4 特殊 Lagna（0.5h）

**文件**: `src/calculator.py` (追加方法)

- Bhava Lagna, Hora Lagna, Ghati Lagna, ViGhati Lagna
- Pranapada Lagna, Sree Lagna, Indu Lagna
- Varnada Lagna, Kunda, Yogi Point, Avayogi Point

### 1.5 Vimshottari Dasha（1h）

**文件**: `src/calculator.py` (追加方法，或独立 `src/dasha.py`)

- Moon Nakshatra → 起始主限
- 120 年完整主限-子限时间线
- 365.25 天/年制
- 当前所在主限和子限标注

**关键点**：
- 这是最复杂的计算之一，建议优先用 PyJHora 的 Dasha 模块
- 再自写 PyJHora 返回结果的 JSON 序列化

### 1.6 Shadbala（1h）

**文件**: `src/shadbala.py` (独立模块)

- Sthana Bala（位置力）— 5 子项
- Dig Bala（方向力）
- Kala Bala（时间力）— 11 子项
- Chestha Bala（运动力）
- Naisargika Bala（自然力）
- Drik Bala（相位力）
- 总合 + 达标判定

### 1.7 Ashtakavarga（0.5h）

**文件**: `src/ashtakavarga.py` (独立模块)

- 7 行星 × 12 宫 = BAV
- SAV = 七层叠加
- Kakshya 排列

### 1.8 Yoga 检测（1h）

**文件**: `src/yogas.py` (独立模块)

- 参考 maitreya8 `Yoga.cpp` + `YogaConfig.cpp` 的规则库
- 至少覆盖：
  - Pancha Mahapurusha Yoga（5 重大人物 Yoga）
  - Raja Yoga（统治 Yoga）
  - Dhana Yoga（财富 Yoga）
  - Chandra Yoga / Ravi Yoga（日月 Yoga）
  - Budha-Aditya Yoga, Gaja Kesari Yoga, Neecha Bhanga Yoga
  - Parivartana Yoga（交换 Yoga）

### 验收：
- [ ] 对 1995-07-21 测试用例，输出与 `vedic-profile.md` 格式一致的完整 JSON
- [ ] 所有行星经度、宫头、Dasha 起始日期与现有数据对账

---

## Phase 2 — 验证对标（1-2h）

### 2.1 与现有数据对账

用 `vedic-profile.md` 中的 1995-07-21 数据作为黄金标准：

| 数据点 | 现有值 | 容忍度 |
|--------|--------|--------|
| Sun 星座/宫位 | 4/11 | 完全一致 |
| Moon 度数 | 22°56' | ±0°01' |
| Asc 度数 | 27°39' | ±0°01' |
| Lahiri 岁差值 | 23.797701° | ±0.0001° |
| Rahu-Rahu 起始 | 2024.02 | ±1 月 |
| SAV 第5宫 | 23 | 完全一致 |
| UL 位置 | 双子/第10宫 | 完全一致 |

### 2.2 与 Jagannatha Hora 7.x 交叉验证

- 同一组出生数据在 JHora 中计算
- 对比行星度数、宫头、Dasha 时间线
- 差异 ≤ 0°01'（行星）/ ≤ 1 天（Dasha）

### 2.3 边界测试

- AC 在星座 0° 边界（如 0°05' Aries）
- AC 在星座 29°55' 边界
- 极地出生（高纬度宫位系统差异大）
- 南半球出生

### 验收：
- [ ] 所有对标数据点在容忍度范围内
- [ ] 边界测试无崩溃或明显错误

---

## Phase 3 — 图表渲染（3-4h）

### 3.1 South Indian D1 图（1.5h）

**文件**: `src/renderer.py`

- 方格外框 + 4×4 网格
- 每个格子标注星座名 + 行星位置
- 上升点特殊标记（斜线/箭头）
- 逆行行星标注 (R)
- 输出 SVG / PNG

### 3.2 North Indian D1 图（1h）

- 菱形网格 12 格
- 上升点在顶部第 1 格
- 星座标签在内角

### 3.3 East Indian D1 图（0.5h）

- 8 方向矩形布局

### 3.4 Dasha 时间线图（0.5h）

- 横向甘特图风格
- 主限用大色块，子限用细分格
- 当前时段高亮

### 3.5 Shadbala 条形图（0.5h）

- 7 行星水平条形图
- 达标线标注
- 总分为主，六力可切换

### 验收：
- [ ] 三种图式 SVG 输出，在浏览器中正确渲染
- [ ] 与 maitreya8 同数据输出图式布局一致
- [ ] SVG 文件大小 < 100 KB

---

## Phase 4 — API 服务（2-3h）

### 4.1 FastAPI 路由（1h）

**文件**: `src/api.py`

```
POST /api/v1/calculate     → 全量星盘 JSON
POST /api/v1/chart/south   → South Indian SVG
POST /api/v1/chart/north   → North Indian SVG
POST /api/v1/chart/east    → East Indian SVG
POST /api/v1/dasha         → Dasha 时间线 JSON + SVG
POST /api/v1/interpret     → LLM 解盘 Markdown
POST /api/v1/full          → 计算 + 图表 + 解读 一键
GET  /api/v1/health        → 健康检查
```

### 4.2 输入验证（0.5h）

Pydantic models (`src/schemas.py`)：
- `BirthData`: 日期/时间/时区/经纬度校验
- `AnalysisRequest`: 分析类型 + 参数校验
- `StarChart`: 输出 Schema（完整，匹配 DATA-SCHEMA.md）

### 4.3 错误处理 + 日志（0.5h）

- 无效日期（如 2月30日）
- 星历文件缺失
- LLM API 超时/错误
- 结构化错误响应

### 4.4 Docker 化（0.5h）

- `Dockerfile` — Python 3.12 + uvicorn
- `docker-compose.yml` — 单容器 + 端口 8000
- 星历文件 COPY 进镜像

### 验收：
- [ ] `curl -X POST localhost:8000/api/v1/calculate -d @sample_birth.json` 返回完整 JSON
- [ ] Swagger UI (`/docs`) 可用
- [ ] `docker compose up` 一键启动

---

## Phase 5 — LLM 解盘（2-3h）

### 5.1 Prompt 模板系统（1h）

**文件**: `templates/` 目录

每个分析类型一个模板文件：

| 模板 | 文件 | 覆盖内容 |
|------|------|---------|
| 本命盘 | `natal.md` | 性格、天赋、挑战、人生主题 |
| 投资 | `investment.md` | 大运投资评级、资产配置、禁区 |
| 感情 | `relationship.md` | 过去回顾、未来窗口、配偶画像 |
| 事业 | `career.md` | 事业方向、时机、风险 |
| 健康 | `health.md` | 体质弱点、有利时期 |

每个模板包含：
- 系统角色设定
- 数据注入区 `{{CHART_DATA}}`
- 约束规则注入 `{{RULES}}`
- 分析任务指令
- 输出格式要求

### 5.2 Rule Engine（0.5h）

**文件**: `src/interpreter.py`

- 加载 RULES.md
- 输出前对 LLM 结果做关键词扫描
- 检测是否包含禁止推导的内容（行业名、平台名、公司名等）
- 标注 `[非盘面信息]` 标记

### 5.3 LLM Client（0.5h）

**文件**: `src/llm_client.py`

- Claude API 封装（默认）
- 支持切换 OpenAI 兼容接口
- 结构化 JSON 输出（用 Claude 的 tool_use / structured output）
- 流式响应支持（用于长报告）

### 5.4 输出后处理（0.5h）

- Markdown 格式化
- 注入图表引用（SVG data URI 或文件路径）
- 摘要提取（前 200 字）

### 验收：
- [ ] 对 1995-07-21 数据生成本命盘解读 ≥ 2000 字
- [ ] 投资分析覆盖大运评级、资产配置、禁区清单
- [ ] 所有输出不包含违规推导（按 RULES.md 自检）
- [ ] API 响应时间（不含 LLM）< 1s
- [ ] LLM 调用耗时 < 30s（流式输出）

---

## Phase 6 — 整机测试（1-2h）

### 6.1 端到端测试

- `POST /full` → 完整流程：计算 → 图表 → 解读
- 用 3 组不同的出生数据测试（不同年代、不同纬度）
- 验证输出完整性

### 6.2 性能测试

- 单次 `/calculate` < 1s
- 并发 10 请求无崩溃
- 星历文件加载只在启动时做一次（不要在每次请求时重读）

### 6.3 输出质量评审

- 用 `investment-advice.md` 和 `relationship-analysis.md` 作为质量基准
- 新系统对同一数据生成的解读应与参考样本在同一档次
- LLM 输出在结构、深度、可操作性三个维度评分

### 验收：
- [ ] 3 组测试数据全部通过
- [ ] 无 crash / 无 500 错误
- [ ] 解读质量 ≥ 参考样本

---

## 后续扩展（不在当前范围）

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 更多分盘 (D2-D60) | P2 | 当前 D1+D9 足够 |
| 卜卦 (Prashna) | P2 | 基于当下时间的天象解读 |
| 合盘 (Synastry) | P3 | 双人盘对比 |
| 流年 (Transit/Gochara) | P3 | 当前行星过宫分析 |
| Web 前端 | P3 | Next.js 界面 |
| 多语言 | P3 | 英文 + 中文 |
| 岁差切换 | P4 | True Chitra / Raman 等 |
| 自定义 Yoga 规则 | P4 | 用户可编辑的 Yoga 检测规则 |

---

## 开工顺序

```
P0 环境搭建 ──→ P1 计算引擎 ──→ P2 验证对标
                                    │
                    ┌───────────────┤
                    ▼               ▼
              P3 图表渲染      P4 API 服务
                    │               │
                    └───────┬───────┘
                            ▼
                      P5 LLM 解盘
                            │
                            ▼
                      P6 整机测试
```

P3 和 P4 可以并行做（依赖 P1 完成即可）。

---

## 文件清单（最终产出）

```
vedic-engine/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
├── ephe/                        # 星历数据 (~40 MB)
│   ├── sepl_18.se1
│   ├── semo_18.se1
│   └── seas_18.se1
├── src/
│   ├── __init__.py
│   ├── api.py                   # FastAPI 路由
│   ├── calculator.py            # VedicCalculator 核心
│   ├── dasha.py                 # Vimshottari Dasha 模块
│   ├── shadbala.py              # Shadbala 模块
│   ├── ashtakavarga.py          # Ashtakavarga 模块
│   ├── yogas.py                 # Yoga 检测模块
│   ├── renderer.py              # ChartRenderer 图表
│   ├── interpreter.py           # InterpretationEngine
│   ├── llm_client.py            # LLM API 封装
│   ├── schemas.py               # Pydantic 数据模型
│   ├── constants.py             # 星座/Nakshatra/Yoga 常量
│   └── utils.py                 # 工具函数
├── templates/
│   ├── natal.md
│   ├── investment.md
│   ├── relationship.md
│   ├── career.md
│   ├── health.md
│   └── rules.md
└── tests/
    ├── test_calculator.py
    ├── test_renderer.py
    ├── test_api.py
    └── fixtures/
        └── sample_birth_1995.json
```
