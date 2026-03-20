---
description: 为任意 Token 创建交易所持仓追踪 Dashboard。用户提供 Token 名称、合约地址、交易所钱包地址，自动生成数据抓取脚本和可视化看板。
argument-hint: "[Token 名称，如 USDC]"
allowed-tools: Bash, Read, Write, Edit, Glob
---

# CEX Token Balance Tracker — 交易所持仓看板生成器

## 你的职责

根据用户提供的信息，从零生成一套完整的交易所 Token 持仓追踪项目，包括：
- 链上余额抓取脚本（Python）
- 每日自动更新 + Git push
- 交互式 HTML 看板（历史数据、变化率、地址悬浮明细）
- 本地定时任务（macOS launchd）

---

## Phase 1 · 信息收集

如果用户没有在消息中提供完整信息，逐一询问以下内容：

### 1.1 基本信息
- **Token 名称**：如 `USDC`、`USDT`、`WBTC`
- **项目目录名**：如 `USDCCEX`（默认用 `{TOKEN}CEX`）

### 1.2 各链合约地址
询问用户该 Token 在哪些链上有合约，并提供合约地址：

| 链 | 示例格式 |
|----|---------|
| Tron (TRC20) | `TXXXXxxxxx...`（34位） |
| Ethereum (ERC20) | `0x...`（42位） |
| BNB Chain (BEP20) | `0x...`（42位） |

> 只需提供有余额的链，没有则跳过。

### 1.3 交易所地址列表
请用户按以下格式提供（可直接粘贴 Etherscan / Tronscan / BSCscan 链接）：

```
交易所名: 链 地址
交易所名: 链 地址
```

示例：
```
HTX: Tron TDToUxX8sH4z6moQpK3ZLAN24eupu2ivA4
HTX: ETH  0x18709e89bd403f470088abdacebe86cc60dda12e
Gate: Tron TBA6CypYJizwA9XdC7Ubgc5F1bxrQ7SqPt
```

也接受直接粘贴浏览器链接，自动解析地址：
- `https://tronscan.org/#/address/TXxx...` → Tron 地址
- `https://etherscan.io/token/0xCONTRACT?a=0xADDRESS` → ETH 地址
- `https://bscscan.com/token/0xCONTRACT?a=0xADDRESS` → BNB 地址

---

## Phase 2 · 解析地址

将用户提供的原始信息整理为结构化数据：

```python
TOKEN_NAME = "USDC"

CONTRACTS = {
    "Tron": "T合约地址",
    "ETH":  "0x合约地址",
    "BNB":  "0x合约地址",
}

EXCHANGES = {
    "HTX": {
        "Tron": ["地址1", "地址2"],
        "ETH":  ["地址1"],
        "BNB":  [],
    },
    "Gate": {
        "Tron": ["地址1"],
        ...
    },
    ...
}
```

整理完后向用户确认：
> "我已整理出以下配置，请确认是否正确：[展示结构化列表]"

---

## Phase 3 · 生成项目

确认无误后，在 `$HOME/{TOKEN}CEX` 目录下生成以下文件：

### 3.1 项目结构

```
{TOKEN}CEX/
├── fetch_data.py       # 链上余额抓取脚本
├── index.html          # 交互式 Dashboard
├── requirements.txt    # Python 依赖
├── run_daily.sh        # 每日定时脚本
├── data/
│   ├── .gitkeep
│   ├── history.json    # 历史数据（自动生成）
│   └── data.js         # 前端数据（自动生成）
└── .claude/
    └── commands/
        └── {token}-tracker.md   # 本 skill 的项目专属版本
```

### 3.2 fetch_data.py 核心逻辑

生成的脚本需包含：

```python
# 基本配置（根据用户输入填充）
TOKEN_NAME = "{TOKEN}"
TOKEN_DECIMALS = 6  # 根据 Token 自动判断（USDC/USDT=6，大多数=18）
CONTRACTS = { ... }
RPC = {
    "ETH": "https://eth.llamarpc.com",
    "BNB": "https://bsc-dataseed.binance.org/",
}
TRONGRID_API = "https://api.trongrid.io"

EXCHANGES = { ... }  # 用户提供的地址

# 函数：Tron TRC20 余额查询
def get_tron_balance(address): ...

# 函数：EVM 链 (ETH/BNB) ERC20 余额查询
def get_evm_balance(rpc_url, contract, wallet): ...

# 函数：保存数据（只保留最新一条的 detail，历史只保 balances）
def save_data(balances, detail): ...

# 函数：生成 data.js 供前端读取
def write_datajs(history): ...

# 函数：自动 git commit + push
def git_push(date): ...
```

### 3.3 index.html Dashboard 功能

必须包含：
- **顶部汇总区**：全部交易所合计 + 各交易所持仓卡片（含占比进度条、较昨日变化率）
- **历史数据表格**：每日一组，按 Tron / ETH / BNB / Total 分行
- **变化指标**：
  - Total 行：每个交易所较昨日 `+0.12%` / `-0.34%`（绿/红色标签）
  - 数据格：较昨日绝对变化 `+1,234` / `-567`
- **地址悬浮明细**：鼠标悬停数字，弹出该交易所该链的所有地址及余额，可点击跳转浏览器

### 3.4 Explorer 链接规则

生成地址明细链接时按以下规则拼接：

| 链 | 链接格式 |
|----|---------|
| Tron | `https://tronscan.org/#/address/{address}` |
| ETH | `https://etherscan.io/token/{contract}?a={address}` |
| BNB | `https://bscscan.com/token/{contract}?a={address}` |

---

## Phase 4 · 初始化 & 测试

```bash
cd ~/{TOKEN}CEX
python3 -m venv venv
source venv/bin/activate
pip install requests
python3 fetch_data.py
```

抓取完成后告知用户：
- 数据是否成功获取
- 哪些地址有余额、哪些为空
- 是否有查询失败的地址

---

## Phase 5 · Git 初始化 & 推送

```bash
cd ~/{TOKEN}CEX
git init && git add -A
git commit -m "Init {TOKEN} CEX balance tracker"
```

询问用户：
> "项目已初始化，是否要推送到 GitHub？请提供仓库地址（或告诉我仓库名，我来生成推送命令）。"

---

## Phase 6 · 定时任务（可选）

询问用户是否需要设置每日自动抓取：
> "是否设置每天 00:00（UTC+8）自动抓取并更新看板？"

若需要，生成 macOS launchd plist 并加载：

```bash
# 生成 ~/Library/LaunchAgents/com.{token}cex.daily.plist
# launchctl load + start
```

---

## 完成后总结

输出以下信息：

```
✅ {TOKEN} CEX Balance Tracker 已创建完成！

📁 项目目录：~/{TOKEN}CEX
📊 本地看板：直接打开 ~/{TOKEN}CEX/index.html
🔗 在线看板：https://{username}.github.io/{TOKEN}CEX/（推送后生效）

每日更新方式：
  方式一：定时任务自动运行（已配置）
  方式二：手动运行 /usdc-tracker（或 cd ~/{TOKEN}CEX && python3 fetch_data.py）

如需添加新地址：编辑 fetch_data.py 中的 EXCHANGES 字典，重新运行即可。
```
