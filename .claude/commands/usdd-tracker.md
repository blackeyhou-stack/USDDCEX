---
description: 抓取各大交易所 USDD 余额并更新看板。当用户想更新 USDD 数据、查看最新交易所持仓、运行每日追踪脚本时使用。
argument-hint: "[可选：--dry-run 仅预览不推送]"
allowed-tools: Bash, Read
---

# USDD CEX Balance Tracker — 余额抓取 & 看板更新

## 职责

自动抓取 Tron、ETH、BNB 三条链上各大交易所（HTX / Gate / Kucoin / Bybit / Mexc / Poloniex / Kraken / Bitmart）的 USDD 余额，写入历史数据，并推送至 GitHub Pages 看板。

---

## Phase 1 · 环境检查

在执行前先验证前置条件：

```bash
# 定位项目目录（优先当前目录，其次常见路径）
[ -f "fetch_data.py" ] && USDD_DIR="$(pwd)" || USDD_DIR="$HOME/USDDCEX"
echo "项目目录：$USDD_DIR"
ls "$USDD_DIR/fetch_data.py" 2>/dev/null && echo "✅ 脚本存在" || echo "❌ 未找到 fetch_data.py"
```

若目录不存在，告知用户：
> `fetch_data.py` 未找到，请先 `cd` 进入 USDDCEX 项目目录，或确认项目路径。

---

## Phase 2 · 执行抓取

```bash
cd "$USDD_DIR" && source venv/bin/activate && python3 fetch_data.py
```

运行时间约 **1–2 分钟**，逐一查询链上地址余额，请耐心等待。

---

## Phase 3 · 解读输出并汇报

从脚本输出中提取关键信息，按以下格式展示：

**正常完成示例：**

```
✅ 数据已更新：2026-03-20

         HTX        Gate      Kucoin       Bybit        Mexc    Poloniex      Kraken     Bitmart
Tron  18,115,672   2,496,171   3,887,752   1,737,030   2,209,983     643,664     164,389      21,318
ETH    3,334,000           —           —           —           —     184,975           —      50,000
BNB    3,196,939           —           —           —           —           —           —      33,470

📊 看板地址：https://blackeyhou-stack.github.io/USDDCEX/
🔗 已自动 commit & push 到 GitHub，运营团队刷新页面即可看到最新数据
```

**如有查询失败（⚠️ 行）：**
- 列出失败的地址和链
- 提示：`建议重新运行一次，ETH RPC 偶发超时属正常现象`

---

## Phase 4 · 结果说明

| 状态 | 含义 |
|------|------|
| `✅ 数据已保存` | 当天数据写入 `data/history.json`，前端 `data/data.js` 已更新 |
| `⚠️ error: Read timed out` | ETH/BNB RPC 超时，该地址本次记为空值，重跑可恢复 |
| `git push` 成功 | GitHub Pages 将在 1 分钟内刷新 |

---

## 注意事项

- 同一天多次运行会**覆盖**当天数据（取最新值）
- 历史数据完整保留，不会被覆盖
- 仅最新一天的数据含地址悬浮明细，历史数据只保留汇总数字
