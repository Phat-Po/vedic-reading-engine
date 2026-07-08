---
name: india-vedic
description: 印度占星排盘解读。当操作者提到：印度占星、吠陀占星、Vedic、看盘、排盘、本命盘、Dasha、大运、星盘、问感情/事业/财运/健康/投资、或 /india-vedic 时使用。
---

# india-vedic

自然语言入口，用于把出生信息转换成 `vedic-calculate` 命令调用，读取
JSON 星盘结果，并输出遵守 `RULES.md` 的 Vedic 解读。

## 预设前提

- 仓库已在本地安装，`vedic-calculate` 可执行
- 优先在仓库根目录运行
- 若本地项目使用 `.venv/`，优先调用 `.venv/bin/vedic-calculate`
- 只依赖盘面数据，不依赖操作者背景

## 需要提取的输入

- 性别：`male` 或 `female`
- 出生日期：`YYYY-MM-DD`
- 出生时间：`HH:MM` 或 `HH:MM:SS`
- 出生地点：城市名
- 分析类型：默认 `natal`

如果信息不全，只追问缺失项。

## 分析类型映射

| 用户表达 | analysis_type |
|---|---|
| 综合、本命、全盘 | `natal` |
| 感情、婚姻、恋爱 | `relationship` |
| 事业、工作、职业 | `career` |
| 财运、投资、钱 | `investment` |
| 健康、身体 | `health` |
| 大运、运势、时机 | `dasha` |
| 占问、卜卦 | `prashna` |

## 常用城市速查

| 城市 | lat | lon | timezone |
|---|---:|---:|---|
| 北京 | 39.90 | 116.41 | `Asia/Shanghai` |
| 上海 | 31.23 | 121.47 | `Asia/Shanghai` |
| 台北 | 25.04 | 121.57 | `Asia/Taipei` |
| 香港 | 22.32 | 114.17 | `Asia/Hong_Kong` |
| 新加坡 | 1.35 | 103.82 | `Asia/Singapore` |
| 东京 | 35.68 | 139.76 | `Asia/Tokyo` |
| 纽约 | 40.71 | -74.01 | `America/New_York` |
| 伦敦 | 51.51 | -0.13 | `Europe/London` |

表内没有的城市，使用 WebSearch 查询 `city latitude longitude timezone`。

## 执行流程

### 1. 先确认输入

在运行前先复述一次：

> 确认一下：性别、出生日期时间、城市、分析类型。对吗？

### 2. 运行计算

不要合并 stdout 和 stderr。JSON 保持在 stdout，SVG 路径日志保持在 stderr。

```bash
mkdir -p output
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
  > /tmp/vedic-chart.json 2>/tmp/vedic-assets.txt
```

如果没有本地 `.venv`，直接用 `vedic-calculate`。

### 3. 提取关键字段

不要直接把整份 JSON 原样塞进回复。按需提取这些 section：

- `meta`
- `input`
- `ayanamsa`
- `panchanga`
- `planets`
- `houses`
- `yogas`
- `shadbala`
- `ashtakavarga`
- `dashas`
- `vargas`
- `karakas`

示例：

```bash
python3 <<'PYEOF'
import json
from pprint import pprint

with open("/tmp/vedic-chart.json", "r", encoding="utf-8") as f:
    data = json.load(f)

pprint({
    "meta": data["meta"],
    "ayanamsa": data["ayanamsa"],
    "current_dasha": data["dashas"]["current"],
})
PYEOF
```

### 4. 展示结果

- 可以用文本摘要或 ASCII 盘面
- 不要把原始 SVG 文件内容直接贴进聊天
- 可以告诉用户 SVG 文件保存在 `output/`

### 5. 撰写解读

必须遵守仓库根目录的 `RULES.md`：

- 只使用盘面数据
- 每个结论都要能回溯到盘面因子
- 不推断具体公司、平台、行业、人名、地名
- 健康、法律、投资只给建议性表达，不做确定性断言

推荐结构：

1. 基本信息
2. 星盘总览
3. 核心格局与 Yoga
4. 行星力量
5. 分析类型专项解读
6. 当前与未来大运窗口
7. 总结

每个核心结论都应采用类似格式：

`结论 <- 盘面依据`

## 回退规则

- 如果缺少 `.se1` 文件，允许使用 Moshier fallback
- 如果地点未知，先补经纬度和时区，再计算
- 如果用户只给大概时间，使用整点并明确标注是近似时间
