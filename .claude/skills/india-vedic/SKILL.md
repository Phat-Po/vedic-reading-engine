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

用 `.venv/bin/python` 跑 CLI，工作目录为项目根。

**重要：stdout 和 stderr 必须分开保存。** 不要用 `2>&1` 合并，会导致 JSON 解析失败。

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
  --output-dir output \
  > /tmp/vedic-chart.json 2>/tmp/vedic-svg.txt
```

**注意**：
- --time 参数默认是 HH:MM:SS，操作者给 HH:MM 时补上 `:00`
- --depth 用 3（三级 dasha：maha-antara-pratyantar），操作者没要求深度就用 3
- 不传 --json-only（需要生成 SVG）
- stdout → `/tmp/vedic-chart.json`（纯 JSON 星盘数据）
- stderr → `/tmp/vedic-svg.txt`（SVG 文件路径日志）
- JSON 输出约 360KB，不要用 Read 直接读全文，用 Python 脚本按需提取关键字段

### 3. 读取星盘

用 Python 脚本从 `/tmp/vedic-chart.json` 按需提取关键字段（分多次调用，每次提取 2-3 个 section，避免超长输出导致截断）。

关键字段：
- `meta` — 引擎版本、星历模式（swiss/moshier）
- `input` — 输入确认（gender, date, time, location）
- `ayanamsa` — 岁差系统（Lahiri）
- `panchanga` — 五支（tithi/vara/nakshatra/yoga/karana）
- `planets` — 10 颗星体 + 上升点（每颗含 sign/house/nakshatra/pada/retrograde）
- `houses` — 12 宫位（system + cusps + house_lords）
- `shadbala` — 六力源行星力量（仅需 total Rupas 值）
- `ashtakavarga` — 八层分数（仅需 sarvashtakavarga）
- `yogas` — 行星格局（仅需 detected=true 的）
- `dashas` — Vimshottari 大运（current + periods 概要）
- `vargas` — 九分盘等（仅需 D9 和各盘 ascendant）
- `karakas` — 七重 karaka

**提取脚本模板**（用 heredoc 传入 Python，避免临时文件）：

```bash
python3 << 'PYEOF'
import json
with open('/tmp/vedic-chart.json') as f:
    data = json.load(f)
# 提取当前需要的 section...
PYEOF
```

### 4. 展示星盘（ASCII 文本图）

**终端无法渲染 SVG/PNG 图片。** 不要用 Read 工具读 SVG 文件——它们会显示为原始代码。

用 Python 生成 ASCII 南印度盘文本图展示给操作者：

```bash
python3 << 'PYEOF'
# 从 JSON 读取 planets，生成 ASCII 南印度盘
# 南印度盘：固定星座位置（双鱼左上→顺时针），houses 叠加显示
# 每个格子显示：星座名 + 落入的行星
import json
with open('/tmp/vedic-chart.json') as f:
    data = json.load(f)

planets = data['planets']

# 按星座分组行星
sign_planets = {i: [] for i in range(12)}
planet_abbr = {
    'sun': 'Su', 'moon': 'Mo', 'mercury': 'Me', 'venus': 'Ve',
    'mars': 'Ma', 'jupiter': 'Ju', 'saturn': 'Sa',
    'rahu': 'Ra', 'ketu': 'Ke',
    'uranus': 'Ur', 'neptune': 'Ne', 'pluto': 'Pl',
}
for pname, pdata in planets.items():
    si = pdata['sign']['index'] - 1  # 0-based
    abbr = planet_abbr.get(pname, pname[:2])
    retro = '(R)' if pdata.get('retrograde') else ''
    sign_planets[si].append(f"{abbr}{retro}")

sign_names = ['白羊♈','金牛♉','双子♊','巨蟹♋','狮子♌','处女♍','天秤♎','天蝎♏','射手♐','摩羯♑','水瓶♒','双鱼♓']

# South Indian layout: signs fixed, Pisces top-left, clockwise
layout = [
    [11, 0, 1, 2],     # 双鱼 白羊 金牛 双子
    [10, None, None, 3],  # 水瓶  -    -   巨蟹
    [9, None, None, 4],   # 摩羯  -    -   狮子
    [8, 7, 6, 5],         # 射手 天蝎 天秤 处女
]

# Ascendant info
asc = planets.get('ascendant', {})
asc_sign_idx = asc.get('sign', {}).get('index', 8) - 1  # 0-based

# Render
print("🪐 南印度盘 (D1 — Rasi)")
print("上升:", asc.get('sign', {}).get('name_en', '?'), asc.get('degree_dms', ''))
print()
for ri, row in enumerate(layout):
    cells = []
    for si in row:
        if si is None:
            cells.append("")
        else:
            p_list = sign_planets.get(si, [])
            p_str = " ".join(p_list) if p_list else ""
            asc_mark = " ↑升" if si == asc_sign_idx else ""
            cells.append(f"{sign_names[si]}{asc_mark}\n{p_str}")
    
    # Print row (up to 2 lines per cell)
    for ln in range(2):
        parts = []
        for c in cells:
            lines = c.split("\n") if c else [""]
            txt = lines[ln] if ln < len(lines) else ""
            parts.append(f"{txt:<14}")
        print("  ".join(parts))
    print()
PYEOF
```

同时告诉操作者 SVG 文件可直接打开：
> SVG 星盘文件在 `output/` 和归档后的 `profiles/<slug>/charts/` 中，可用浏览器打开查看：
> ```bash
> open profiles/<slug>/charts/south.svg
> ```

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

## 一、基本信息
- 性别/出生时间/地点/坐标/时区
- Lahiri 岁差系统
- 上升星座 + 月亮星座 + 当前大运
- 五支 (Panchanga)

## 二、星盘总览
- ASCII 南印度盘文本图
- 行星分布摘要表（sign, house, degree, nakshatra, retrograde）
- 宫位分布表

## 三、核心格局
- 检测到的 Yogas（列出名称、含义、强度、证据）
- Pancha Mahapurusha 等特殊格局
- 上升/月亮关键配置

## 四、行星力量 (Shadbala)
- Shadbala 排行表（从最强到最弱）
- 最强/最弱行星分析

## 五、[分析类型专项解读]
- 本命(natal)：性格、天赋、挑战、人生主题
- 事业(career)：10宫 + 10宫主 + 太阳/土星/水星配置 + D10分盘
- 感情(relationship)：7宫 + 7宫主 + 金星配置 + D9分盘
- 投资(investment)：2/5/9/11宫 + 木星配置
- 健康(health)：1/6/8/12宫 + 火星/土星配置

## 六、大运关键节点
- 当前大运（Maha-Antara-Pratyantar 三级）
- 未来 5 年大运窗口概览
- 有利/不利时段

## 七、Karaka 解读
- 七重 karaka 表格 + 简要解读

## 八、总结
- 3-5 个核心结论（每个带星盘因子引用 ←）
- 需要留意的领域
```

### 6. 解读深度控制

操作者说"简单看看"→ 只出 ASCII 星盘 + 核心格局 + 一段总结（精简模式）。
操作者说"详细分析"或未说明 → 出完整报告（标准模式）。

## 错误处理

- 缺少 ephe 文件 → 自动 fallback Moshier 模式，在报告中注明
- 坐标/时区不确定 → 先问操作者确认
- 计算失败 → 报告错误信息，不要瞎编
- JSON 解析失败（Extra data 错误）→ 说明 stdout/stderr 未分开，重跑并确保 `> file.json 2>file.txt`

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
# 3. 写 report.md（完整解读报告，图片引用使用相对路径 charts/xxx.svg）
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

归档完成后，自动将 report.md 转为手机友好 PDF。

**前置检查：系统可用内存**（Chrome headless 需要 ~300MB 空闲 RAM）：

```bash
python3 -c "import subprocess; vm=subprocess.run(['vm_stat'],capture_output=True,text=True).stdout; free=int([l for l in vm.split('\n') if 'Pages free' in l][0].split(':')[1].strip().rstrip('.')); mb=free*16384/1024/1024; print(f'{mb:.0f} MB free'); print('OK' if mb>400 else 'LOW_MEMORY')"
```

若可用内存 < 400 MB，告知操作者：
> ⚠️ 系统空闲 RAM 不足，Chrome 可能被系统强制终止。建议关掉一些应用后重试，或手动运行：
> ```bash
> cd /Volumes/轻松打爆你/VIBE\ CODING/10_PROJECTS_ACTIVE/20260707__tool__vedic-reading
> .venv/bin/vedic-pdf "profiles/<slug>/report.md"
> ```

若内存充足，运行 PDF 生成：

```bash
cd /Volumes/轻松打爆你/VIBE\ CODING/10_PROJECTS_ACTIVE/20260707__tool__vedic-reading
.venv/bin/vedic-pdf "profiles/<slug>/report.md"
```

PDF 输出到 `profiles/<slug>/report.pdf`。

**技术说明**（2026-07-07 已修复）：`vedic-pdf` 现在会自动将报告中的相对路径图片（`charts/xxx.svg`）转换为 base64 data URI 嵌入 HTML，Chrome 无需访问原始文件即可渲染。修复代码在 `src/vedic_engine/pdf_exporter.py` 的 `_embed_images()` 函数。

若 PDF 生成失败：
- SIGKILL / 进程被杀死 → 内存不足，见上方前置检查
- 文件存在但图片空白 → 极不可能（已 base64 内嵌），检查 SVG 源文件是否有效

## Hard Rules

- 只输出星盘数据里有的信息，不编造
- 每个星盘结论必须可追溯到 JSON 中的具体字段
- 不推荐具体投资标的、医疗方案、法律行动
- 输出语言跟随操作者输入语言（操作者用中文则输出中文）
- **解读完成后必须归档到 profiles/，不可跳过**
- **终端无法渲染 SVG/PNG 图片** — 用 ASCII 文本图展示星盘，告知操作者 SVG 文件路径可用浏览器打开
- **stdout 和 stderr 必须分开保存** — 不要用 `2>&1`，用 `> file.json 2>file.txt`
