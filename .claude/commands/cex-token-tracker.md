---
name: cex-token-tracker
description: "为任意 Token 创建交易所持仓追踪 Dashboard。用户提供 Token 名称、合约地址、交易所钱包地址，自动生成链上数据抓取脚本和可视化看板。Use when tracking exchange holdings for any on-chain token, monitoring stablecoin distribution across CEXs, or building a daily balance dashboard."
argument-hint: "[Token 名称，如 USDC]"
allowed-tools: Bash, Read, Write, Edit, Glob
---

# CEX Token Balance Tracker

从用户提供的 Token 信息和交易所地址，生成完整的链上持仓追踪项目。

## Workflow

**Step 1 · 收集信息**

询问用户提供：
- Token 名称和各链合约地址（Tron TRC20 / ETH ERC20 / BNB BEP20）
- 各交易所的钱包地址（接受浏览器链接自动解析）
- 项目名称（默认 `{TOKEN}CEX`）

确认整理后的结构化配置，无误再继续。

**Step 2 · 生成项目**

在 `~/{TOKEN}CEX/` 下创建：
- `fetch_data.py`：多链余额抓取，完成后自动 git commit & push
- `index.html`：交互式 Dashboard，含历史表格、变化率标签、地址悬浮明细
- `run_daily.sh`：每日定时脚本
- `requirements.txt`：仅需 `requests`

**Step 3 · 地址链接解析规则**

| 链接格式 | 解析结果 |
|---------|---------|
| `tronscan.org/#/address/TXxx` | Tron 地址 |
| `etherscan.io/token/0xCONTRACT?a=0xADDR` | ETH 地址 |
| `bscscan.com/token/0xCONTRACT?a=0xADDR` | BNB 地址 |

**Step 4 · 初次运行验证**

```bash
cd ~/{TOKEN}CEX
python3 -m venv venv && source venv/bin/activate
pip install requests && python3 fetch_data.py
```

展示抓取结果，标注有余额的地址和失败地址，确认数据正确。

**Step 5 · Git & GitHub Pages**

初始化仓库，推送 GitHub，配置 GitHub Pages，输出在线看板链接。

**Step 6 · 定时任务（可选）**

询问是否配置每天 00:00 UTC+8 自动抓取，通过 macOS launchd 实现，兼容锁屏和 Power Nap。

## Key Principles

- Token 精度：USDC / USDT 为 6 位，大多数 Token 为 18 位，不确定时询问用户
- ETH RPC：`https://eth.llamarpc.com`，BNB RPC：`https://bsc-dataseed.binance.org/`
- Tron：`https://api.trongrid.io/v1/accounts/{address}`
- 只有最新一条数据保留地址明细（`detail`），历史条目仅保留汇总数字
