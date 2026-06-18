"""
批量下载股票池数据（分批下载，避免 API 限流）
运行: python download_data.py
"""
import time
from data.fetcher import fetch_batch
from data.universe import get_blue_chip_symbols

symbols = get_blue_chip_symbols()
total = len(symbols)
batch_size = 40  # 每批 40 只

print(f"准备下载 {total} 只股票，分 {(total-1)//batch_size + 1} 批")
print(f"tickflow 限速 10 次/分钟，每批 40 只 ≈ 4.5 分钟\n")

all_results = {}
for i in range(0, total, batch_size):
    batch = symbols[i:i+batch_size]
    batch_num = i // batch_size + 1
    print(f"\n{'='*50}")
    print(f"📦 第 {batch_num} 批: {len(batch)} 只")
    print(f"{'='*50}")

    results = fetch_batch(batch, delay=7)
    all_results.update(results)

    # 批次之间休息 60 秒（让限速窗口重置）
    if i + batch_size < total:
        print(f"\n⏸️  休息 60 秒后下载下一批...")
        time.sleep(60)

print(f"\n{'='*50}")
print(f"📦 全部完成: 成功 {len(all_results)}/{total}")
print(f"数据保存目录: datasets/")
