---
name: cex-token-tracker
description: "为任意 Token 创建交易所持仓追踪 Dashboard。用户提供 Token 名称、合约地址、各交易所钱包地址，自动生成链上数据抓取脚本和可视化看板。Use when tracking exchange holdings for any on-chain token, monitoring stablecoin distribution across CEXs, or building a daily balance dashboard."
---

# CEX Token Balance Tracker — 交易所持仓看板生成器

## Purpose

根据用户提供的 Token 信息和交易所地址，从零生成一套完整的链上持仓追踪系统。支持 Tron、Ethereum、BNB Chain 三条链，自动抓取链上余额，生成带历史对比、变化率和地址明细的可视化 Dashboard，并部署到 GitHub Pages 供团队每日查看。

---

## How It Works

### Step 1: 收集 Token 基本信息

询问用户提供：

- **Token 名称**：如 `USDC`、`USDT`、`WBTC`
- **各链合约地址**（只需填有余额的链）：
  - Tron TRC20：`TXxx...`（34位）
  - Ethereum ERC20：`0x...`（42位）
  - BNB Chain BEP20：`0x...`（42位）
- **项目名称**：默认使用 `{TOKEN}CEX`，如 `USDCCEX`

### Step 2: 收集交易所地址

接受以下任意格式，自动解析链和地址：

- 直接粘贴浏览器链接：
  - `https://tronscan.org/#/address/TXxx...` → Tron
  - `https://etherscan.io/token/0xCONTRACT?a=0xADDRESS` → ETH
  - `https://bscscan.com/token/0xCONTRACT?a=0xADDRESS` → BNB
- 直接填写地址：`HTX: Tron TDToUxX8sH4z6...`

整理完成后向用户确认结构化配置，无误后继续。

### Step 3: 生成项目文件

在 `~/{TOKEN}CEX/` 目录下创建完整项目：

- `fetch_data.py` — 链上余额抓取脚本，支持 Tron / ETH / BNB 多链并发查询
- `index.html` — 交互式 Dashboard，含历史表格、变化率、地址悬浮明细
- `run_daily.sh` — 每日定时运行脚本，完成后自动 git commit & push
- `requirements.txt` — Python 依赖（仅需 `requests`）
- `.claude/commands/{token}-tracker.md` — 项目专属的数据更新 skill

### Step 4: 初次运行 & 验证数据

```bash
cd ~/{TOKEN}CEX
python3 -m venv venv && source venv/bin/activate
pip install requests
python3 fetch_data.py
```

展示抓取结果，标注有余额的地址和查询失败的地址，确认数据准确。

### Step 5: Git 初始化 & 推送

初始化本地仓库，询问是否推送 GitHub，提供推送命令并配置 GitHub Pages，生成可分享的在线看板链接。

### Step 6: 配置每日定时任务（可选）

在 macOS 上通过 launchd 配置每天 00:00（UTC+8）自动抓取并推送，兼容锁屏和 Power Nap 待机状态。

---

## Usage Examples

**示例 1：USDC 交易所持仓追踪**

```
我想做一个 USDC 在各大交易所的持仓 Dashboard

USDC 合约：
- ETH: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
- BNB: 0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d

交易所地址：
https://etherscan.io/token/0xA0b86991c...?a=0x5041ed759dd4afc3a72b8192c143f72f4724081
https://etherscan.io/token/0xA0b86991c...?a=0x28c6c06298d514db089934071355e5743bf21d60
```

**示例 2：多链 USDT 持仓监控**

```
做一个 USDT 在 Tron 和 ETH 链上的交易所存量追踪

Tron 合约：TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
ETH 合约：0xdAC17F958D2ee523a2206206994597C13D831ec7

交易所：
Binance Tron: TNXoiAJ3dct8Fjg4M9fkLFh9S2v9TXc32K
Binance ETH:  0x28c6c06298d514db089934071355e5743bf21d60
OKX Tron:     TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf
```

**示例 3：追加新交易所地址**

```
我的 USDC Dashboard 已经建好了，帮我在 HTX 下面加一个新的 ETH 地址：
0x1234abcd...
```

---

## Key Capabilities

- **多链支持**：Tron TRC20 / Ethereum ERC20 / BNB Chain BEP20 同时查询
- **自动解析链接**：直接粘贴 Tronscan / Etherscan / BSCscan 链接，自动提取链和地址
- **历史数据保留**：每日数据累积，支持长期趋势对比
- **变化率指标**：Total 行显示较昨日百分比变化（绿涨红跌），数据格显示绝对变化量
- **地址悬浮明细**：鼠标悬停数字，弹出各地址余额明细，可点击跳转区块链浏览器
- **自动推送**：每次抓取完成后自动 git commit & push，GitHub Pages 1分钟内刷新
- **定时任务**：macOS launchd 每日自动执行，锁屏/待机（Power Nap）下也可触发

## Tips for Best Results

1. **提供合约地址**：确保提供的是 Token 合约地址，而非钱包地址
2. **区分链**：一个交易所在不同链上可能有多个地址，全部提供可得到更准确的汇总
3. **粘贴浏览器链接**：比手填地址更准确，可直接从 Etherscan / Tronscan 复制
4. **确认 Token 精度**：USDC/USDT 精度为 6，大多数 Token 为 18，如不确定告知我
5. **初次运行后验证**：将抓取结果与浏览器上的实际余额核对，确保数据无误

---

## Output Format

项目创建完成后，你会得到：

- **本地项目目录**：`~/{TOKEN}CEX/`，含所有源码和数据文件
- **本地看板**：直接打开 `index.html` 即可查看（无需服务器）
- **在线看板**：`https://{username}.github.io/{TOKEN}CEX/`（推送后生效）
- **每日更新 skill**：`/{token}-tracker`，随时手动触发数据更新
- **定时任务**：每天 00:00 UTC+8 自动抓取并推送（可选）

---

### Related

- [Etherscan Token Tracker](https://etherscan.io/tokens) — 查询 ERC20 合约地址
- [Tronscan](https://tronscan.org) — 查询 TRC20 钱包余额
- [BSCscan](https://bscscan.com) — 查询 BEP20 合约地址
