# PRD — Vedic 卜卦系统 (Vedic Divination Engine)

生成日期: 2026-07-06
状态: 规划中（未开工）

---

## 一、产品定义

### 1.1 是什么

一个**自托管的 Vedic 占星计算 + AI 解盘系统**。输入出生时间和地点，自动完成从天文计算到自然语言解盘的全流程。

区别于：
- **在线计算器**（如 astrosage.com）：只能看数据，不给深度解读
- **桌面软件**（如 Jagannatha Hora）：数据全但不解释
- **通用 LLM**：不懂真实天文计算，幻觉严重

### 1.2 核心价值

```
天文精确性（Swiss Ephemeris + Lahiri 岁差）
    +
传统 Jyotish 逻辑（Yoga / Dasha / Shadbala / Ashtakavarga）
    +
LLM 结构化解盘（遵循 RULES.md 防污染规则）
    =
可信的 Vedic AI 占星师
```

### 1.3 使用场景

| 场景 | 输入 | 输出 |
|------|------|------|
| 本命盘解读 | 出生日期+时间+经纬度 | 完整星盘 JSON + 自然语言解读 |
| 大运预测 | 同上 + 目标时间段 | 主限-子限时间线 + 各时段评级 |
| 专项分析 | 同上 + 分析主题（投资/感情/事业） | 针对性的 LLM 报告 |
| 卜卦 (Prashna) | 提问时间+地点 | 基于当下天象的卜卦解读（未来） |

---

## 二、功能范围

### Phase 1 — 计算引擎（MVP 核心）

| 功能 | 说明 |
|------|------|
| 行星位置计算 | 日月水金火土木天海冥 + 罗喉计都 (Rahu/Ketu)，视位置 |
| 岁差 | **Lahiri**（固定），值动态计算 |
| 宫位系统 | Placidus（默认），可选 Equal / Koch / Whole Sign |
| D1 主盘 (Rasi) | 星座、宫位、度数、Nakshatra + Pada、宿主 |
| Panchanga 五支历 | Tithi, Vara, Nakshatra, Yoga, Karana |
| 特殊 Lagna | Bhava Lagna, Hora Lagna, Ghati Lagna, Sree Lagna, Indu Lagna 等 |
| Upagraha 虚点 | Dhuma, Vyatipaata, Gulika, Maandi 等 11 个 |
| Vimshottari Dasha | 120 年主限 + 子限（基于 Moon Nakshatra） |
| Shadbala | 六力计算（Sthana, Dig, Kala, Chestha, Naisargika, Drik） |
| Ashtakavarga | SAV (Sarvashtakavarga) + BAV (Bhinna) |
| Yoga 检测 | Ravi Yoga, Chandra Yoga, Raja Yoga, Dhana Yoga 等 |
| Nakshatra 详细 | 27 宿 + Pada 级别 |

### Phase 2 — 图表渲染

| 功能 | 说明 |
|------|------|
| South Indian 图 | 默认，方块固定星座 |
| North Indian 图 | 菱形，上升点置顶 |
| East Indian 图 | 8 方向矩形 |
| Dasha 时间线 | 可视化大运-子限时间段 |
| Shadbala 条形图 | 行星强度对比 |
| SAV 热力图 | 宫位吉凶分布 |

### Phase 3 — AI 解盘

| 功能 | 说明 |
|------|------|
| 本命盘解读 | 性格、天赋、挑战、人生主题 |
| 大运预测 | 时段化的人生阶段分析 |
| 专项分析 | 投资 / 感情 / 事业 / 健康（遵循 RULES.md） |
| 卜卦 (Prashna) | 即时天象解读（未来 Phase 4） |

---

## 三、技术选型

| 层 | 技术 | 理由 |
|----|------|------|
| 天文计算 | `pyswisseph` (v2.10.3.2+) | 官方 Swiss Ephemeris Python 绑定，精度最高 |
| Vedic 高级逻辑 | `PyJHora` + 自写补充 | PyJHora 覆盖大运/Yoga/分盘，不足部分参考 maitreya8 公式自写 |
| 图渲染 | `matplotlib` + `svgwrite` | 南/北/东印度图式需要自定义逻辑，SVG 输出兼容 web |
| 后端 API | Python FastAPI | 轻量、异步、自文档化 |
| LLM 解盘 | Claude API / OpenAI API | 需要理解复杂提示词和长上下文 |
| 前端（可选） | Next.js + TailwindCSS | 仅当需要 web 界面时 |
| 部署 | Docker + VPS | 与现有 Lightnode 基础设施对齐 |

---

## 四、数据输入输出

### 输入

```json
{
  "name": "string (optional)",
  "birth": {
    "date": "1995-07-21",
    "time": "11:35:00",
    "timezone": "Asia/Taipei",
    "latitude": 25.0378,
    "longitude": 121.5650
  },
  "analysis_type": "natal | dasha | investment | relationship | career | prashna",
  "ayanamsa": "lahiri"
}
```

### 输出

与现有 `vedic-profile.md` 结构兼容的 JSON，详见 `DATA-SCHEMA.md`。

---

## 五、反污染规则（继承自 RULES.md）

AI 解盘时必须：
1. 仅使用盘面数据作为推理依据
2. 每个结论标注推导来源
3. 不推导具体行业/平台/产品/公司
4. 输出前自检：「如果我不知道这个人是谁，是否仍会给出这条推荐？」
5. 如使用了盘主自述背景，必须标注 `[非盘面信息]`

---

## 六、验收标准

- [ ] 计算精度与 Jagannatha Hora 7.x 一致（Lahiri 岁差，1995-07-21 样本比对）
- [ ] South Indian D1 图可渲染为 SVG
- [ ] Vimshottari Dasha 时间线与现有 vedic-profile 数据一致
- [ ] Shadbala / SAV 值与现有参考数据一致
- [ ] LLM 输出遵守 RULES.md 全部约束
- [ ] API 响应时间 < 3 秒（不含 LLM）
