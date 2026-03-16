#!/usr/bin/env python3
"""
USDD CEX Balance Tracker
自动从 Tron / ETH / BSC 链上抓取各交易所 USDD 余额
"""

import requests
import json
import os
import time
from datetime import datetime

# ─── USDD 合约地址 ────────────────────────────────────────────────────────────
USDD_CONTRACT = {
    "Tron": "TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz",
    "ETH":  "0x4f8e5de400de08b164e7421b3ee387f461becd1a",
    "BNB":  "0x45E51bc23D592EB2DBA86da3985299f7895d66Ba",
}

# ─── RPC 节点 ─────────────────────────────────────────────────────────────────
RPC = {
    "ETH": "https://eth.llamarpc.com",
    "BNB": "https://bsc-dataseed.binance.org/",
}
TRONGRID = "https://api.trongrid.io"

# ─── 交易所钱包地址 ────────────────────────────────────────────────────────────
EXCHANGES = {
    "HTX": {
        "Tron": [
            "TDToUxX8sH4z6moQpK3ZLAN24eupu2ivA4",
            "TK86Qm97uM848dMk8G7xNbJB7zG1uW3h1n",
            "TFTWNgDBkQ5wQoP8RXpRznnHvAVV8x5jLu",
        ],
        "ETH": [
            "0x18709e89bd403f470088abdacebe86cc60dda12e",
            "0xa03400e098f4421b34a3a44a1b4e571419517687",
            "0x4fb312915b779b1339388e14b6d079741ca83128",
        ],
        "BNB": [
            "0xafdfd157d9361e621e476036fee62f688450692b",
            "0x18709e89bd403f470088abdacebe86cc60dda12e",
            "0xdd3cb5c974601bc3974d908ea4a86020f9999e0c",
        ],
    },
    "Gate": {
        "Tron": ["TBA6CypYJizwA9XdC7Ubgc5F1bxrQ7SqPt"],
        "ETH":  [],
        "BNB":  [],
    },
    "Kucoin": {
        "Tron": [
            "TL17qUCWc9ZRjYvxyihC3uteUCYBn48S3S",
            "TUFhdQLH8MLCN9fVpiJ5pHVPbED3x8ZF5V",
            "TUpHuDkiCCmwaTZBHZvQdwWzGNm5t8J2b9",
        ],
        "ETH": [],
        "BNB": [],
    },
    "Bybit": {
        "Tron": ["TU4vEruvZwLLkSfV9bNw12EJTPvNr7Pvaa"],
        "ETH":  [],
        "BNB":  [],
    },
    "Mexc": {
        "Tron": ["TEPSrSYPDSQ7yXpMFPq91Fb1QEWpMkRGfn"],
        "ETH":  [],
        "BNB":  [],
    },
    "Poloniex": {
        "Tron": ["TUgSgCQL6pMSy9zByn4sgxqrJa95sZExBG"],
        "ETH":  [
            "0x29065a4c1f2f20d1e263930088890d6f49fe715a",
            "0x8fca4ade3a517133ff23ca55cdaea29c78c990b8",
        ],
        "BNB":  [],
    },
    "Kraken": {
        "Tron": ["TG2CMGxnTPgQ6V58kiKd7wbyN8ewtAmY76"],
        "ETH":  [],
        "BNB":  [],
    },
    "Bitmart": {
        "Tron": ["TA7jHA7BR17Sv4vdV2Thx2wJaiUGHNybzU"],
        "ETH":  ["0x6d0d19bdddc5ed1dd501430c9621dd37ebd9062d"],
        "BNB":  ["0xa23ef2319ba4c933ebfdba80c332664a6cb13f1a"],
    },
}

EXCHANGE_LIST = ["HTX", "Gate", "Kucoin", "Bybit", "Mexc", "Poloniex", "Kraken", "Bitmart"]
CHAIN_LIST    = ["Tron", "ETH", "BNB"]


# ─── 链上查询函数 ──────────────────────────────────────────────────────────────

def get_tron_usdd_balance(address: str) -> float | None:
    """通过 Trongrid API 获取 Tron 地址的 USDD 余额"""
    try:
        url = f"{TRONGRID}/v1/accounts/{address}"
        resp = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        data = resp.json()
        if not data.get("data"):
            return 0.0
        account = data["data"][0]
        contract = USDD_CONTRACT["Tron"]
        for token in account.get("trc20", []):
            if contract in token:
                return int(token[contract]) / 1e18
        return 0.0
    except Exception as e:
        print(f"  ⚠️  Tron {address[:10]}… error: {e}")
        return None


def get_evm_usdd_balance(chain: str, wallet: str) -> float | None:
    """通过公共 RPC 获取 ETH/BSC 地址的 USDD 余额（无需 API Key）"""
    try:
        contract = USDD_CONTRACT[chain]
        # balanceOf(address) selector = 0x70a08231
        padded = wallet[2:].lower().zfill(64)
        payload = {
            "jsonrpc": "2.0",
            "method":  "eth_call",
            "params":  [{"to": contract, "data": "0x70a08231" + padded}, "latest"],
            "id":      1,
        }
        resp = requests.post(RPC[chain], json=payload, timeout=15)
        result = resp.json().get("result", "0x0")
        return int(result, 16) / 1e18
    except Exception as e:
        print(f"  ⚠️  {chain} {wallet[:10]}… error: {e}")
        return None


# ─── 主逻辑 ───────────────────────────────────────────────────────────────────

def fetch_all_balances() -> dict:
    result = {}
    for ex in EXCHANGE_LIST:
        result[ex] = {}
        for chain in CHAIN_LIST:
            addrs = EXCHANGES[ex].get(chain, [])
            if not addrs:
                result[ex][chain] = None
                continue
            total, has_error = 0.0, False
            for addr in addrs:
                print(f"  → {ex} / {chain} / {addr[:12]}…")
                if chain == "Tron":
                    bal = get_tron_usdd_balance(addr)
                else:
                    bal = get_evm_usdd_balance(chain, addr)
                if bal is None:
                    has_error = True
                else:
                    total += bal
                time.sleep(0.4)   # 避免限速
            result[ex][chain] = None if has_error else round(total)
    return result


def save_data(balances: dict):
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 读取历史
    history_path = os.path.join(data_dir, "history.json")
    history = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    history = [h for h in history if h["date"] != today]
    history.append({"date": today, "balances": balances})
    history.sort(key=lambda x: x["date"], reverse=True)

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # 同时生成 data.js 供前端直接读取（无需本地服务器）
    js_path = os.path.join(data_dir, "data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by fetch_data.py — do not edit manually\n")
        f.write(f"const USDD_HISTORY = {json.dumps(history, indent=2, ensure_ascii=False)};\n")

    print(f"\n✅ 数据已保存：{today}")


def print_summary(balances: dict):
    print("\n─── 本次抓取汇总 ───────────────────────────────")
    print(f"{'':12}", end="")
    for ex in EXCHANGE_LIST:
        print(f"{ex:>12}", end="")
    print()
    for chain in CHAIN_LIST:
        print(f"{chain:<12}", end="")
        for ex in EXCHANGE_LIST:
            val = balances[ex][chain]
            s = f"{val:,}" if val is not None else "-"
            print(f"{s:>12}", end="")
        print()


def main():
    print("🔍 开始抓取 USDD 余额...\n")
    balances = fetch_all_balances()
    print_summary(balances)
    save_data(balances)
    print("📊 打开 index.html 查看看板\n")


if __name__ == "__main__":
    main()
