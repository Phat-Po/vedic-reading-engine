# Vedic Engine — Tier 1 & 2 升级计划

## Context

当前 Vedic reading 引擎的 Shadbala、Ashtakavarga、Yoga、Aspects 都是 placeholder/scaffold 级别（硬编码、空数组、玩具公式）。此外 Varga 只有 D9、Dasha 只有两层、日出日落写死、没有行运功能。需要把 Tier 1（4 个 placeholder → 真实算法）和 Tier 2（6 个新功能）全部实现。

## 改动范围

5 个文件，~1,955 行新代码：

| 文件 | 改动量 | 改动内容 |
|------|--------|---------|
| `constants.py` | +580 行 | 所有查找表：ASPECTS、EXALTATION、NAISARGIKA_BALA、PLANET_FRIENDS/GENDER、DIG_BALA_HOUSES、SHADBALA_COMPONENTS_ZH、BAV_RULES(672 int)、YOGA_DEFINITIONS、VARGA_META |
| `calculator.py` | +1,090 行 | 重写 4 个方法 + 新增 ~15 个方法 |
| `schemas.py` | +25 行 | TransitRequest、dasha_depth 字段 |
| `api.py` | +60 行 | transit 端点、depth 参数、vimshopaka 集成 |
| `tests/test_calculator.py` | +200 行 | ~17 个新测试 |

无新依赖，只使用现有 `pyswisseph==2.10.3.2`。

## 实施顺序（12 个 Phase，按依赖关系排列）

### Tier 1: 替换 Placeholder → 真实算法

**Phase 1 — 先行：constants.py 常量表**
一次性加入 Tier 1 所有需要的常量表（ASPECTS, EXALTATION, PLANET_FRIENDS 等）。

**Phase 2 — Drishti 相位** (~110 行)
- 替换 `_calc_aspects`：全行星整宫相位（Mars +4/7/8，Jupiter +5/7/9，Saturn +3/7/10，Rahu/Ketu +5/7/9 可选）
- 输出：每行星 `aspects[]` + `aspected_by[]`
- 测试：验证 Jupiter(Scorpio/8) 投射到 5th(Pisces)、7th(Taurus)、9th(Cancer)
- **被 Phase 3, 5 依赖**

**Phase 3 — Shadbala 六力** (~330 行，最大单功能)
- 重写 `_calc_shadbala`：6 个子力各一个 sub-method
  - Sthana Bala: Uccha + Saptavargaja(简化版，D1 only) + Ojayugma + Kendradi + Drekkana
  - Dig Bala: 标准方向力（60 virupa at 极值宫）
  - Kala Bala: Nathonnatha(昼夜) + Paksha(月相) + Tribhaga(日三分) + Abda/Masa/Vara/Hora + Ayana(偏角)
  - Chestha Bala: 逆行加分，Mercury/Venus 特殊 elongation 公式
  - Naisargika Bala: 固定值（Sun=60, Moon=51, Venus=43...）
  - Drik Bala: 基于 Phase 2 Drishti 的吉凶星相位加减
- 输出：`total_virupas` → `total_rupa`(/60)，`meets_minimum`(>= 5 rupa)，`status: "full-calculation"`
- 测试：Sun 在 Cancer 4° → uccha bala 应该低（远离 Aries 10° 旺点），rupa 在 3-7 范围
- **依赖 Phase 1, 2**

**Phase 4 — Ashtakavarga (BAV + SAV)** (~260 行)
- 重写 `_calc_ashtakavarga`：
  - 8 个参考点 × 7 行星 × 12 宫 = 672 个 bindu 值，来自 `BAV_RULES` 常量表
  - Rotation logic：参考点所在宫 → "宫1"，旋转 12 值数组
  - SAV = 7 个 BAV 按宫求和
  - Trikona Shodhana + Ekadhipatya Shodhana 精简
- 输出：`bhinna_ashtakavarga(7 planets × 12 houses)` + `sarvashtakavarga` + `trikona_shodhana`
- 测试：SAV 总和 ~330，BAV 每宫 0-8，SAV house 5 接近 23(golden 值)
- **被 Phase 10 依赖**

**Phase 5 — Yoga 检测** (~350 行)
- 重写 `_detect_yogas`：规则引擎，每个 yoga 一个 `_check_*` 方法
- 检测 ~20 种瑜伽：
  - Pancha Mahapurusha × 5（Ruchaka/Bhadra/Hamsa/Malavya/Sasa）
  - Gaja Kesari / Kemadruma / Neecha Bhanga / Parivartana
  - Chandra Mangala / Adhi Yoga / Sunapha/Anapha/Durudhara
  - Amala / Sakata / Viparita Raja / Dhana Yoga / Raja Yoga
  - 保留已有的 Mercury-Venus Conjunction / Budha-Aditya
- 输出：每个 yoga `{name, name_zh, category, detected, strength, evidence}`
- 测试：样本盘应检测到 Mercury-Venus，检测不到 Budha-Aditya（不同星座）
- **依赖 Phase 1, 2**

### Tier 2: 新功能

**Phase 6 — 更多 Varga (D2, D3, D7, D10, D12, D30)** (~150 行)
- 扩展 `_calc_vargas`：每个 varga 一个 `_varga_{key}` 子方法
- 各分盘映射公式（BPHS 标准）：D2(两分), D3(三分/Decanate), D7(七分), D10(十分/Dasamsa), D12(十二分), D30(三十分/Trimsamsa)
- 测试：Sun(Cancer 4° odd sign) → D10 part 2 → Leo(5)
- **被 Phase 7 依赖**

**Phase 7 — Vimshopaka Bala** (~80 行)
- 新增 `_calc_vimshopaka_bala`：行星在各 varga 的星座关系评分 × 权重
- 权重：D1=3.5, D9=3.0, D10=1.5, D2=1.0, D3=1.0, D30=1.0, D7/D12=0.5
- 覆盖 10.5/20 权重，标记 `partial`
- 集成到 `calculate()` → 顶层 `vimshopaka_bala`
- 测试：Sun(D1=Cancer=friend, D9=Leo=own) → 总分 > 0
- **依赖 Phase 1, 6**

**Phase 8 — 真实日出日落** (~40 行)
- 替换 `_sunrise_sunset_placeholder`：用 `swe.rise_trans()` 计算实际日出日落
- 新增 `_jd_to_datetime` 工具方法
- 保留 placeholder fallback（当 ephemeris 文件不全时）
- 测试：1995-07-21 台北 → 日出 ~05:20 ± 5min, 日落 ~18:40 ± 5min

**Phase 9 — 更深 Dasha 层级** (~90 行)
- 扩展 `_calc_vimshottari`：depth 参数(2/3/4)
- 递归 `_sub_periods()`：Pratyantar(第3层) + Sookshma(第4层)
- 优化：depth=4 时只计算当前 mahadasha 以下，避免 JSON 爆炸
- Schema: `CalculateRequest.dasha_depth: int = 2`
- API: `/api/v1/dasha` 接受 depth 参数
- 测试：depth=3 → antardasha 含 `pratyantar` key，depth=4 → 含 `sookshma`

**Phase 10 — Gochara 行运** (~150 行)
- 新增 `_calc_gochara` + API `/api/v1/transit`
- 计算目标日期的行星位置，覆盖到 natal chart
- 特殊分析：Sade Sati(土星过月)、Rahu-Ketu 轴线、Jupiter/Saturn 行运
- 行运-本命合相检测(3° orb)
- Schema: `TransitRequest(birth: BirthData, target_date, target_time)`
- 测试：2026-07-07 对样本盘 → Saturn 在 Pisces(12th from Moon Aries=Phase 1 Sade Sati)
- **依赖 Phase 4**

**Phase 11 — Ashtakavarga 行运评分** (~20 行)
- 在 `_calc_gochara` 里加 `_bav_transit_quality`：行运行星经过宫位的 BAV bindu 数 → very_positive/positive/neutral/challenging
- **依赖 Phase 4, 10**

**Phase 12 — 收尾** 
- API/schema 集成验证
- 所有现有测试回归
- `calculate()` meta version → "0.2.0"
- Shadbala/Ashtakavarga status → "full-calculation"
- 全量 golden-value 验证

## 验证方案

1. **每个 Phase 完成后**：`pytest -q`（全量回归 + 新增测试）
2. **全程保持**：`ruff check src tests`
3. **关键节点**（Phase 3, 4, 12 后）：`vedic-calculate --sample` 输出有效性检查
4. **最终验证**：启动 `uvicorn` → `POST /api/v1/full` → 确认结构完整 + 无 placeholder status
5. **向后兼容**：所有现有 JSON key 不变，只增加新 key

## 关键风险

1. **BAV 表转录错误**：672 个整数，最少交叉参考 2 个来源
2. **Shadbala Saptavargaja 简化**：因 varga 不全(只做 D1)，先做 D1-only 版，标记 `saptavargaja-simplified-d1-only`
3. **swe.rise_trans 可能失败**：始终保留 fallback
4. **Dasha depth=4 JSON 膨胀**：只计算当前 mahadasha 的子层
