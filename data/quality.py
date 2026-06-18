"""
data/quality.py
数据质量检查与清洗模块

功能：
  - 检查 symbol/name 是否为空 → 标记待人工确认
  - 价格/成交量空值 → 向前填充 + 向后填充
  - 停牌日（volume=0）→ 删除整行（Backtrader 自动跳过，不产生假信号）
  - 数据行数不足检测
  - 输出结构化质量报告
"""
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check_data_quality(symbols: list[str]) -> tuple[list[str], list[str], dict]:
    """
    对已下载的股票数据做完整性检查与清洗

    原则：
      - 不随意删除股票，发现问题标记出来供人工辨认
      - symbol/name 为空 → 标记待人工确认
      - 价格/成交量空值 → 向前填充 + 向后填充
      - 停牌日（volume=0）→ 删除整行，让 Backtrader 自动跳过
      - 清洗后回写 CSV

    参数
    ----
    symbols : 候选股票代码列表

    返回
    ----
    (全部股票列表, 需人工确认的列表, 质量报告 dict)
    """
    from data.fetcher import load_csv, save_csv

    need_review = []   # 需要人工确认的股票
    report = {"total": 0, "clean": 0, "filled": 0, "review": 0, "no_data": 0}
    print(f"🔍 数据完整性检查与清洗")
    print(f"-" * 50)

    for symbol in symbols:
        report["total"] += 1
        try:
            df = load_csv(symbol)
        except FileNotFoundError:
            print(f"  ⚠️  {symbol}: 无本地数据")
            report["no_data"] += 1
            continue

        if df.empty:
            print(f"  ⚠️  {symbol}: 空数据")
            need_review.append(symbol)
            report["review"] += 1
            continue

        issues = []

        # 检查 1: symbol/name 是否为空
        if "symbol" in df.columns:
            null_symbol = df["symbol"].isna().sum()
            if null_symbol > 0:
                issues.append(f"symbol列有 {null_symbol} 个空值")

        if "name" in df.columns:
            null_name = df["name"].isna().sum()
            if null_name > 0:
                issues.append(f"name列有 {null_name} 个空值")

        # 检查 2: 价格/成交量空值统计
        price_cols = ["open", "high", "low", "close", "volume", "amount"]
        available_cols = [c for c in price_cols if c in df.columns]
        total_nulls = df[available_cols].isna().sum().sum()

        if total_nulls > 0:
            issues.append(f"价格/量数据共 {total_nulls} 个空值")

            # 填充：先向前填充，再向后填充
            df[available_cols] = df[available_cols].ffill().bfill()

            # 检查填充后是否仍有空值（整行都是 NaN 的情况）
            remaining = df[available_cols].isna().sum().sum()
            if remaining > 0:
                issues.append(f"填充后仍有 {remaining} 个空值")

        # 检查 3: 停牌日删除（volume == 0 的整行删掉）
        modified = False
        if "volume" in df.columns:
            suspended = df[df["volume"] == 0]
            if len(suspended) > 0:
                suspend_dates = suspended["trade_date"].tolist() if "trade_date" in df.columns else []
                df = df[df["volume"] != 0].reset_index(drop=True)
                issues.append(f"删除 {len(suspended)} 天停牌数据（volume=0）")
                modified = True

        # 检查 4: 数据行数是否过少
        if len(df) < 60:
            issues.append(f"数据仅 {len(df)} 行，不足 60 天")

        # 处理结果
        if issues:
            # 判断是否需要人工确认
            needs_human = any(
                "symbol列" in i or "name列" in i or "填充后仍有" in i
                for i in issues
            )

            if needs_human:
                need_review.append(symbol)
                report["review"] += 1
                status = "🟡 待人工确认"
            else:
                report["filled"] += 1
                status = "🔧 已清洗"

            # 如果有填充或删除操作，回写 CSV
            if total_nulls > 0 or modified:
                save_csv(df, symbol)

            print(f"  {status} {symbol}: {'; '.join(issues)}")
        else:
            report["clean"] += 1
            print(f"  ✅ {symbol}: 数据完整（{len(df)} 行）")

    # 汇总报告
    print(f"-" * 50)
    print(f"📋 数据质量报告:")
    print(f"   总计: {report['total']} 只")
    print(f"   完整: {report['clean']} 只")
    print(f"   已填充: {report['filled']} 只")
    print(f"   待人工确认: {report['review']} 只")
    print(f"   无数据: {report['no_data']} 只")
    if need_review:
        print(f"\n⚠️  以下股票需要人工检查:")
        for s in need_review:
            print(f"   - {s}")

    return symbols, need_review, report


# ==================== 快速测试 ====================
if __name__ == "__main__":
    from data.universe import get_blue_chip_symbols

    symbols = get_blue_chip_symbols(10)
    print(f"测试前 10 只: {symbols}\n")
    all_symbols, need_review, report = check_data_quality(symbols)
