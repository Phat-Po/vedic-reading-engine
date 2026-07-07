---
name: india-vedic
description: 印度占星排盘解读。当操作者提到：印度占星、吠陀占星、Vedic、看盘、排盘、本命盘、Dasha、大运、星盘、问感情/事业/财运/健康/投资、或 /india-vedic 时使用。
---

# india-vedic — 印度占星排盘与解读

本项目的唯一自然语言入口。接收自然语言输入，解析后调用 vedic-calculate
计算星盘 + 生成 SVG，再用 Claude 自身的吠陀占星知识写出解读报告。

## 输入信息要求

必须从操作者输入中提取：
- **性别**：男(male) / 女(female)
- **出生日期**：YYYY-MM-DD
- **出生时间**：HH:MM（若操作者只说大概时间如"早上8点多"，取 08:00 并在报告注明）
- **出生地点**：城市名 → 查坐标(lat/lon)和时区
- **分析类型**：从语境推断，默认为 natal

### 城市坐标与时区对照（常用）

操作者说中文城市名时，用此表查坐标和时区。表内没有的城市，用 WebSearch
查"城市名 latitude longitude timezone"获取。

| 城市 | lat | lon | timezone |
|------|-----|-----|----------|
| 北京 | 39.90 | 116.41 | Asia/Shanghai |
| 上海 | 31.23 | 121.47 | Asia/Shanghai |
| 广州 | 23.13 | 113.26 | Asia/Shanghai |
| 深圳 | 22.54 | 114.06 | Asia/Shanghai |
| 台北 | 25.04 | 121.57 | Asia/Taipei |
| 香港 | 22.32 | 114.17 | Asia/Hong_Kong |
| 东京 | 35.68 | 139.76 | Asia/Tokyo |
| 新加坡 | 1.35 | 103.82 | Asia/Singapore |
| 吉隆坡 | 3.14 | 101.69 | Asia/Kuala_Lumpur |
| 曼谷 | 13.75 | 100.50 | Asia/Bangkok |
| 新德里 | 28.61 | 77.23 | Asia/Kolkata |
| 孟买 | 19.08 | 72.88 | Asia/Kolkata |
| 伦敦 | 51.51 | -0.13 | Europe/London |
| 纽约 | 40.71 | -74.01 | America/New_York |
| 洛杉矶 | 34.05 | -118.24 | America/Los_Angeles |
| 悉尼 | -33.87 | 151.21 | Australia/Sydney |
| 墨尔本 | -37.81 | 144.96 | Australia/Melbourne |

### 分析类型映射

| 操作者说的 | analysis_type |
|-----------|--------------|
| 综合/本命/全盘/看一下/算算 | natal |
| 感情/婚姻/恋爱 | relationship |
| 事业/工作/职业 | career |
| 财运/投资/钱 | investment |
| 健康/身体 | health |
| 大运/运势/时机 | dasha |
| 卜卦/占问 | prashna |

若无法确定，默认用 natal。

## 执行流程

### 1. 确认输入

提取出生信息后，先用一句话向操作者确认：

> 确认一下：**男/女**，**YYYY年M月D日 HH:MM**，**城市名** (lat, lon)，看**分析类型中文**。对吗？

操作者确认后再跑。若缺信息，只问缺的那项。

### 2. 计算星盘

用 `.venv/bin/python` 跑 CLI，工作目录为项目根：

```bash
cd /Volumes/轻松打爆你/VIBE\ CODING/10_PROJECTS_ACTIVE/20260707__tool__vedic-reading
.venv/bin/vedic-calculate \
  --date <YYYY-MM-DD> \
  --time <HH:MM:SS> \
  --tz <timezone> \
  --lat <latitude> \
  --lon <longitude> \
  --gender <male|female> \
  --type <analysis_type> \
  --depth 3 \
  --output-dir output
```

**注意**：
- --time 参数默认是 HH:MM:SS，操作者给 HH:MM 时补上 `:00`
- --depth 用 3（三级 dasha：maha-antara-pratyantar），操作者没要求深度就用 3
- 不传 --json-only（需要生成 SVG）
- 命令输出：stdout 是 JSON（星盘数据），stderr 是 SVG 文件路径

### 3. 读取星盘

将 stdout 的 JSON 解析为星盘数据。关键字段：
- `input` — 输入确认（gender, date, time, location）
- `ayanamsa` — 岁差系统（Lahiri）
- `panchanga` — 五支（tithi/vara/nakshatra/yoga/karana）
- `planets` — 10 颗星体 + 上升点（每颗含 sign/house/nakshatra/pada/retrograde）
- `houses` — 12 宫位
- `shadbala` — 六力源行星力量
- `ashtakavarga` — 八层分数
- `yogas` — 行星格局（已检测）
- `dashas` — Vimshottari 大运（current + periods + antardashas）
- `vargas` — 九分盘等
- `karakas` — 七重 karaka

### 4. 展示星盘 SVG

星盘 SVG 存在 `output/` 下，用 Read 工具读取后展示给操作者：
- `output/<slug>-south.svg` — 南印度盘
- `output/<slug>-north.svg` — 北印度盘
- `output/<slug>-east.svg` — 东印度盘
- `output/<slug>-dasha.svg` — Dasha 时间线
- `output/<slug>-shadbala.svg` — 行星力量柱状图

### 5. 撰写解读报告

用 Claude 自身的吠陀占星知识，基于星盘数据撰写报告。**不使用 LLM API**。

解读时必须遵循：
- **每个结论必须引用星盘数据**，格式：`结论 ← 星盘因子`（如：事业运强 ← 10宫主在1宫 + 太阳在MC）
- **反污染规则**：不推断具体行业（如 Shopee/Amazon）、不推断具体公司名、不推断具体人名地名
- **不绝对断言**：用"倾向""暗示""可能"而非"一定""必然"
- **健康/法律/投资类保持建议性**，不做诊断或投资建议

报告结构（根据 analysis_type 调整重点）：

```
# 印度占星解读报告

## 基本信息
- 性别/出生时间/地点/坐标/时区
- Lahiri 岁差系统
- 上升星座 + 月亮星座 + 当前大运

## 星盘总览
- 南印度盘 + 北印度盘 SVG
- 行星分布摘要表（sign, house, nakshatra, retrograde）

## 核心格局
- 检测到的 Yogas（列出名称、含义、强度）
- Pancha Mahapurusha 等特殊格局
- 上升/月亮关键配置

## 行星力量 (Shadbala)
- Dasha 时间线 SVG
- Shadbala 柱状图 SVG
- 最强/最弱行星分析

## [分析类型专项解读]
- 本命(natal)：性格、天赋、挑战、人生主题
- 事业(career)：10宫 + 10宫主 + 太阳/土星/水星配置 + D10分盘
- 感情(relationship)：7宫 + 7宫主 + 金星配置 + D9分盘
- 投资(investment)：2/5/9/11宫 + 木星配置
- 健康(health)：1/6/8/12宫 + 火星/土星配置

## 大运关键节点
- 当前大运（Maha-Antara-Pratyantar 三级）
- 未来 5 年大运窗口
- 有利/不利时段

## 总结
- 3-5 个核心结论（每个带星盘因子引用）
- 需要留意的领域
```

### 6. 解读深度控制

操作者说"简单看看"→ 只出星盘 + 核心格局 + 一段总结（精简模式）。
操作者说"详细分析"或未说明 → 出完整报告（标准模式）。

## 错误处理

- 缺少 ephe 文件 → 自动 fallback Moshier 模式，在报告中注明
- 坐标/时区不确定 → 先问操作者确认
- 计算失败 → 报告错误信息，不要瞎编

### 7. 归档存档

解读报告写完后，**必须**将本次排盘所有文件归档到 `profiles/` 目录。

#### 目录结构

```
profiles/<YYYYMMDD>_<name>/
├── input.json        # 输入信息（name/gender/date/time/timezone/lat/lon/city/analysis_type）
├── chart.json        # 精简星盘 JSON（meta/input/ayanamsa/panchanga/planets/houses/karakas/yogas(仅detected)/shadbala/ashtakavarga(仅sarva)/dashas(仅current+periods概要)）
├── report.md         # 解读报告全文
└── charts/
    ├── south.svg
    ├── north.svg
    ├── east.svg
    ├── shadbala.svg
    └── dasha.svg
```

#### 归档步骤

```bash
SLUG="<YYYYMMDD>_<name>"   # 如 1997-01-04_徐闹闹
PROFILES_DIR="profiles"

mkdir -p "$PROFILES_DIR/$SLUG/charts"

# 1. 写 input.json（从本次解析的输入信息）
# 2. 写 chart.json（从 stdout JSON 提取关键字段）
# 3. 复制 report.md
# 4. 复制 output/ 下的 SVG 到 charts/
cp output/chart-south.svg "$PROFILES_DIR/$SLUG/charts/south.svg"
cp output/chart-north.svg "$PROFILES_DIR/$SLUG/charts/north.svg"
cp output/chart-east.svg "$PROFILES_DIR/$SLUG/charts/east.svg"
cp output/chart-shadbala.svg "$PROFILES_DIR/$SLUG/charts/shadbala.svg"
cp output/chart-dasha.svg "$PROFILES_DIR/$SLUG/charts/dasha.svg"
```

#### 更新 INDEX.md

在 `profiles/INDEX.md` 表格最上方插入一行：

```markdown
| YYYY-MM-DD | [名字](./<slug>/report.md) | 出生日期 | 上升星座 度数 | 月亮星座 度数 | 分析类型 | 当前大运 | [PDF](./<slug>/report.pdf) |
```

INDEX.md 表格按算盘日期倒序排列（最新的在最上面）。

#### Slug 规则
- 格式：`<出生日期>_<名字>`，如 `1997-01-04_徐闹闹`
- 出生日期从 input 中取，格式 YYYY-MM-DD
- 名字用操作者输入的名字（中文直接用，英文用拼音）
- 若同一人多次算不同主题，在 slug 后加分析类型：`1997-01-04_徐闹闹_career`

### 8. 生成 PDF

归档完成后，自动将 report.md 转为手机友好 PDF：

```bash
cd /Volumes/轻松打爆你/VIBE\ CODING/10_PROJECTS_ACTIVE/20260707__tool__vedic-reading
.venv/bin/vedic-pdf "profiles/<slug>/report.md"
```

PDF 输出到 `profiles/<slug>/report.pdf`。生成后用 SendUserFile 发送给操作者。

若 Chrome 未安装或 PDF 生成失败，跳过并告知操作者手动运行 `vedic-pdf`。

## Hard Rules

- 只输出星盘数据里有的信息，不编造
- 每个星盘结论必须可追溯到 JSON 中的具体字段
- 不推荐具体投资标的、医疗方案、法律行动
- 输出语言跟随操作者输入语言（操作者用中文则输出中文）
- SVG 文件路径必须正确，Read 前先确认文件存在
- **解读完成后必须归档到 profiles/，不可跳过**
