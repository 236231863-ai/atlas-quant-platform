"""Fetch real lottery historical data from official Sporttery API.

Source: https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry
Games:
  - 85  = 超级大乐透 (DLT)  front:5 from 1-35, back:2 from 1-12
  - 235 = 双色球 (SSQ)     front:6 from 1-33, back:1 from 1-16
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

API = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
GAMES = {"85": ("dlt", "大乐透"), "235": ("ssq", "双色球")}
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://static.sporttery.cn/"}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_page(game_no: str, page_no: int, page_size: int = 30) -> dict:
    url = (
        f"{API}?gameNo={game_no}&provinceId=0&pageSize={page_size}"
        f"&isVerify=1&pageNo={page_no}"
    )
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_draw(result: str) -> str:
    """'10 11 18 22 35 06 12' -> '10,11,18,22,35|06,12'"""
    parts = result.split()
    return "|".join([" ".join(parts[:5]), " ".join(parts[5:])])


def fetch_all(game_no: str, target: int = 520) -> list:
    rows = []
    page = 1
    while len(rows) < target:
        data = fetch_page(game_no, page)
        value = (data.get("value") or {}).get("list") or []
        if not value:
            break
        for item in value:
            num = item.get("lotteryDrawNum", "")
            result = item.get("lotteryDrawResult", "")
            dt = item.get("lotteryDrawTime", "")
            pool = item.get("poolBalanceAfterdraw", "")
            if num and result:
                rows.append([num, dt, parse_draw(result), pool])
        print(f"  page {page}: +{len(value)} (累计 {len(rows)})")
        page += 1
        time.sleep(0.4)
    return rows[:target]


def main() -> None:
    for game_no, (code, name) in GAMES.items():
        print(f"抓取 {name} (gameNo={game_no}) ...")
        rows = fetch_all(game_no, target=520)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        out = RAW_DIR / f"{code}_history.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["issue", "date", "numbers", "pool"])
            w.writerows(rows)
        print(f"  -> {out} : {len(rows)} 期")
    print("完成。")


if __name__ == "__main__":
    sys.exit(main())
