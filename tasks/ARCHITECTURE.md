# 架构设计 — Vedic 卜卦系统

生成日期: 2026-07-06
状态: 草案 v1

---

## 一、总体架构

```
┌──────────────────────────────────────────────────┐
│                   用户接口层                      │
│  ┌──────────────┐  ┌──────────────┐              │
│  │  CLI (初期)   │  │  Web (后期)   │             │
│  │  Python 脚本  │  │  Next.js SPA │             │
│  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                       │
│         └────────┬────────┘                       │
│                  │ REST / JSON                     │
├──────────────────▼───────────────────────────────┤
│                  API 网关层                        │
│  ┌──────────────────────────────────────┐        │
│  │           FastAPI Server              │        │
│  │  /calculate   → 星盘计算              │        │
│  │  /chart       → 图表 SVG              │        │
│  │  /interpret   → LLM 解盘              │        │
│  │  /full        → 一键全流程            │        │
│  └──────┬───────────────────────────────┘        │
│         │                                         │
├─────────┼─────────────────────────────────────────┤
│         │          计算引擎层                      │
│  ┌──────▼──────────────────────────────────┐     │
│  │         VedicCalculator                 │     │
│  │                                         │     │
│  │  ┌─────────────┐  ┌───────────────┐    │     │
│  │  │ pyswisseph  │  │   PyJHora     │    │     │
│  │  │ (SwissEph)  │  │ (Dasha/Yoga/  │    │     │
│  │  │ 行星+宫位   │  │  Ashtakavarga │    │     │
│  │  │ +岁差+交点  │  │  /Panchanga)  │    │     │
│  │  └──────┬──────┘  └───────┬───────┘    │     │
│  │         │                 │             │     │
│  │         └────────┬────────┘             │     │
│  │                  │                       │     │
│  │  ┌───────────────▼──────────────────┐   │     │
│  │  │     Custom Vedic Modules         │   │     │
│  │  │  (参考 maitreya8 公式自写补充)    │   │     │
│  │  │  · Upagraha 计算                │   │     │
│  │  │  · 特殊 Lagna 计算              │   │     │
│  │  │  · Jaimini Karaka               │   │     │
│  │  │  · Yoga 引擎（扩展 PyJHora）     │   │     │
│  │  └──────────────────────────────────┘   │     │
│  └──────────────────────────────────────────┘     │
│                                                   │
├───────────────────────────────────────────────────┤
│                  AI 解释层                         │
│  ┌──────────────────────────────────────┐        │
│  │         InterpretationEngine         │        │
│  │  ┌────────────┐  ┌───────────────┐  │        │
│  │  │ Prompt     │  │  Rule Engine  │  │        │
│  │  │ Templates  │  │  (RULES.md    │  │        │
│  │  │ 按分析类型 │  │   约束检查)    │  │        │
│  │  └────────────┘  └───────────────┘  │        │
│  │  ┌────────────────────────────────┐  │        │
│  │  │       LLM API Client           │  │        │
│  │  │   Claude / GPT / 本地模型       │  │        │
│  │  └────────────────────────────────┘  │        │
│  └──────────────────────────────────────┘        │
│                                                   │
├───────────────────────────────────────────────────┤
│                  渲染层                            │
│  ┌──────────────────────────────────────┐        │
│  │         ChartRenderer                │        │
│  │  · SouthIndianRenderer              │        │
│  │  · NorthIndianRenderer              │        │
│  │  · EastIndianRenderer               │        │
│  │  · DashaTimelineRenderer            │        │
│  │  · ShadbalaBarRenderer              │        │
│  │  → 输出 SVG (可嵌入 HTML)            │        │
│  └──────────────────────────────────────┘        │
│                                                   │
├───────────────────────────────────────────────────┤
│                  数据层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ StarChart│  │  Dasha   │  │ Interpretation│  │
│  │  JSON    │  │ Timeline │  │    Report     │  │
│  │          │  │  JSON    │  │   Markdown    │  │
│  └──────────┘  └──────────┘  └──────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Swiss Ephemeris 星历文件 (ephe/)        │    │
│  │  · sepl_18.se1 (行星)                    │    │
│  │  · semo_18.se1 (月亮)                    │    │
│  │  · seas_18.se1 (小行星)                  │    │
│  │  · 约 40 MB，需随项目分发或下载           │    │
│  └──────────────────────────────────────────┘    │
└───────────────────────────────────────────────────┘
```

---

## 二、核心模块详解

### 2.1 计算引擎 — VedicCalculator

**类设计**：

```python
class VedicCalculator:
    """核心计算器，包装 pyswisseph + PyJHora"""

    def __init__(self, ayanamsa: str = "lahiri"):
        # 初始化 Swiss Ephemeris，设置星历路径
        # 设置岁差模式

    def calculate(self, birth: BirthData) -> StarChart:
        """主入口：根据出生数据计算完整星盘"""

    # 内部方法
    def _calc_planets(self, jd: float) -> dict[str, PlanetPosition]
    def _calc_houses(self, jd: float, lat: float, lon: float) -> dict[int, HouseCusp]
    def _calc_panchanga(self, jd: float) -> Panchanga
    def _calc_upagrahas(self, planets: dict) -> dict[str, Upagraha]
    def _calc_special_lagnas(self, jd: float, lat: float, lon: float) -> dict[str, Lagna]
    def _calc_dasha(self, moon_nakshatra: str, moon_pada: int) -> DashaTimeline
    def _calc_shadbala(self, planets: dict, houses: dict) -> dict[str, ShadbalaResult]
    def _calc_ashtakavarga(self, planets: dict) -> AshtakavargaResult
    def _detect_yogas(self, planets: dict, houses: dict, lagnas: dict) -> list[Yoga]
```

**岁差管理**：

```python
AYANAMSA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "true_chitra": swe.SIDM_TRUE_CITRA,   # 仅 SE 2.10+
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
    # ... 其他按需添加
}

def set_ayanamsa(self, name: str):
    sid = self.AYANAMSA_MAP[name]
    swe.set_sid_mode(sid, 0, 0)
```

**默认固化为 Lahiri**，通过常量锁定，避免误改。

### 2.2 解释引擎 — InterpretationEngine

```python
class InterpretationEngine:
    """LLM 驱动的解盘引擎"""

    def __init__(self, llm_client, rules_path: str = "RULES.md"):
        self.rules = load_rules(rules_path)
        self.prompts = load_prompt_templates()

    def interpret(self, chart: StarChart,
                  analysis_type: str) -> InterpretationReport:
        """
        1. 根据 analysis_type 选择 Prompt 模板
        2. 将 StarChart JSON 关键字段注入 Prompt
        3. 附加 RULES.md 约束
        4. 调用 LLM
        5. 后处理：自检规则合规性
        6. 返回 Markdown 报告
        """
```

**Prompt 模板结构**：

```
你是 Vedic 占星师。基于以下星盘数据进行解读。

## 星盘数据
{chart_json_summary}

## 约束规则
{rules_content}

## 分析任务
{analysis_type_instruction}

## 输出格式
{output_format_spec}
```

### 2.3 图表渲染 — ChartRenderer

三种图式的布局逻辑（参考 maitreya8 `VedicRasiChart.cpp`）：

**South Indian（方块网格）**：
```
┌──┬──┬──┬──┐
│10│11│12│1 │
├──┼──┼──┼──┤
│9 │  │  │2 │
├──┼──┼──┼──┤
│8 │  │  │3 │
├──┼──┼──┼──┤
│7 │6 │5 │4 │
└──┴──┴──┴──┘
```
星座位置固定，不随上升点旋转。上升点用标记（箭头/斜线）标出。

**North Indian（菱形网格）**：
```
    ▲
   ╱ ╲
  ╱ 1 ╲
 ╱12   2╲
▕11  ◇  3▏
 ╲10   4╱
  ╲ 9 ╱
   ╲ ╱
    ▼
```
上升点始终在顶部（第 1 宫）。星座按顺序排列。

**East Indian（8方向矩形）**：
```
┌────┬────┬────┐
│ 11 │ 12 │ 1  │
├────┼────┼────┤
│ 10 │ 中心│ 2  │
├────┼────┼────┤
│ 9  │ 8  │ 3  │
├────┴────┴────┤
│  4   5   6   7  │
└───────────────┘
```
上升点未必在顶，按实际天宫方向排列。

### 2.4 API 设计

```
POST /api/v1/calculate
  → 全量星盘计算，返回 StarChart JSON

POST /api/v1/chart/{style}
  → style: south|north|east
  → 返回 SVG 字符串

POST /api/v1/interpret
  → Body: { chart_id, analysis_type }
  → 返回 Markdown 报告

POST /api/v1/full
  → 一键：计算 + 图表 + 解读
  → 返回完整响应包

GET /api/v1/health
  → 服务状态 + 星历文件检查
```

---

## 三、数据流

```
用户输入 (birth data)
    │
    ▼
VedicCalculator.calculate()
    │
    ├── pyswisseph: 行星经度、宫头
    ├── PyJHora: Dasha 时间线
    ├── 自写模块: Upagraha、特殊 Lagna、Yoga
    │
    ▼
StarChart (JSON, ~5KB)
    │
    ├──→ ChartRenderer → SVG
    │
    └──→ InterpretationEngine
            │
            ├── Prompt 组装
            ├── LLM API 调用
            ├── 规则自检
            │
            ▼
        InterpretationReport (Markdown, ~5-20KB)
```

---

## 四、部署架构

```
Docker Container
├── Python 3.12
├── pyswisseph + PyJHora
├── FastAPI (uvicorn)
├── Swiss Ephemeris 星历文件 (ephe/)
├── Prompt 模板 (templates/)
└── 规则文件 (RULES.md)

端口: 8000
健康检查: GET /api/v1/health
```

初期可跑在本地 macOS，后期迁移到 Lightnode VPS 或 Fly.io。

---

## 五、关键决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 岁差 | Lahiri（固定） | 印度标准，与现有数据兼容，与主流软件一致 |
| 黄道制 | 恒星黄道 (Sidereal) | Vedic 标准 |
| 交点算法 | 真交点 (True Node) | 与现有数据一致 |
| 行星位置 | 视位置 (Apparent) | 与现有数据一致 |
| 大运年天数 | 365.25 天 | Vimshottari 标准 |
| 图式默认 | South Indian | 最传统，使用最广 |
| 主语言 | Python | 最大生态 + pyswisseph 支持 |
| LLM 提供商 | Claude API | 长上下文 + 多语言 + 结构化输出能力强 |
| 星历文件 | 随项目分发 | 避免运行时下载，保证离线可用 |

---

## 六、参考资源

| 资源 | 用途 |
|------|------|
| maitreya8 (`src/jyotish/`) | Yoga 公式、Dasha 算法、Upagraha 计算参考 |
| maitreya8 (`src/gui/VedicRasiChart.cpp`) | 三种图式布局逻辑参考 |
| maitreya8 (`src/base/maitreya.h`) | AYANAMSA 枚举、Rasi 枚举、数据结构参考 |
| `pyswisseph` 文档 | Swiss Ephemeris Python API |
| `PyJHora` 源码 | Vedic 高级逻辑实现参考 |
| `vedic-profile.md` | 输出数据格式蓝本 |
| `RULES.md` | LLM 解盘反污染约束 |
| `investment-advice.md` / `relationship-analysis.md` | LLM 解盘输出质量参考样本 |
