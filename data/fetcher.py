"""
data/fetcher.py
行情数据获取模块

使用 tickflow API 下载 A 股日线 K 线数据，保存为 CSV。
支持：
  - 单只股票下载
  - 批量下载（带进度显示和限速）
  - 增量更新（只下载新数据）
"""
import sys
import time
import datetime
import pandas as pd
from pathlib import Path

# 将项目根目录加入搜索路径，确保能 import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tickflow import TickFlow
import config


def _get_tickflow() -> TickFlow:
    """初始化 tickflow 客户端"""
    return TickFlow(api_key=config.API_KEY)


def _date_to_ms(date_str: str) -> int:
    """日期字符串 'YYYY-MM-DD' → 毫秒时间戳"""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)


def _ms_to_date(ms: int) -> str:
    """毫秒时间戳 → 日期字符串 'YYYY-MM-DD'"""
    dt = datetime.datetime.fromtimestamp(ms / 1000)
    return dt.strftime("%Y-%m-%d")


def fetch_single(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    adjust: str = "forward",
) -> pd.DataFrame: #返回值类型注解
    """
    下载单只股票的日线 K 线数据

    参数
    ----
    symbol : 股票代码，如 '600519.SH'
    start_date : 起始日期 'YYYY-MM-DD'，默认取 config.BACKTEST['start_date']
    end_date : 结束日期 'YYYY-MM-DD'，默认取 config.BACKTEST['end_date']
    adjust : 复权方式，'forward'（前复权）/ 'backward'（后复权）/ None（不复权）

    返回
    ----
    pd.DataFrame，列包含 date, open, high, low, close, volume, amount
    """
    if start_date is None:
        start_date = config.BACKTEST["start_date"]
    if end_date is None:
        end_date = config.BACKTEST["end_date"]

    tf = _get_tickflow()
    start_ms = _date_to_ms(start_date)
    end_ms = _date_to_ms(end_date)

    df = tf.klines.get(
        symbol,
        period="1d",
        start_time=start_ms,
        end_time=end_ms,
        adjust=adjust,
        count=10000,  # tickflow 默认只返回 100 条，必须显式设大
        as_dataframe=True,
    )

    if df is None or df.empty:
        print(f"⚠️  {symbol}: 无数据（{start_date} ~ {end_date}）")
        return pd.DataFrame()

    # 只保留核心列（symbol/name 便于识别股票，trade_date 是日期）
    keep_cols = ["trade_date", "symbol", "name", "open", "high", "low", "close", "volume", "amount"]
    available = [c for c in keep_cols if c in df.columns]
    df = df[available].copy()

    # 日期列转为 datetime 类型
    if "trade_date" in df.columns:
        df["trade_date"] = pd.to_datetime(df["trade_date"])

    print(f"✅ {symbol}: {len(df)} 条记录（{start_date} ~ {end_date}）")
    return df


def save_csv(df: pd.DataFrame, symbol: str) -> Path:
    """
    将 DataFrame 保存为 CSV 文件

    参数
    ----
    df : 股票数据
    symbol : 股票代码（用于生成文件名）

    返回
    ----
    保存路径
    """
    filename = f"{symbol.replace('.', '_')}.csv"
    path = config.DATA_DIR / filename
    df.to_csv(path, index=False)
    return path


def fetch_and_save(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
) -> Path | None:
    """
    下载单只股票数据并保存为 CSV

    参数
    ----
    symbol : 股票代码
    start_date, end_date : 日期范围

    返回
    ----
    保存的文件路径，下载失败返回 None
    """
    df = fetch_single(symbol, start_date, end_date)
    if df.empty:
        return None
    path = save_csv(df, symbol)
    return path


def fetch_batch(
    symbols: list[str],
    start_date: str = None,
    end_date: str = None,
    delay: float = 0.5,
) -> dict[str, pd.DataFrame]:
    """
    批量下载多只股票数据

    参数
    ----
    symbols : 股票代码列表
    start_date, end_date : 日期范围
    delay : 每次请求间隔（秒），避免被限速

    返回
    ----
    dict，key=股票代码，value=DataFrame
    """
    results = {}
    total = len(symbols)

    print(f"📥 开始批量下载 {total} 只股票...")
    print(f"   日期范围: {start_date or config.BACKTEST['start_date']} "
          f"~ {end_date or config.BACKTEST['end_date']}")
    print("-" * 50)

    for i, symbol in enumerate(symbols, 1):
        try:
            df = fetch_single(symbol, start_date, end_date)
            if not df.empty:
                save_csv(df, symbol)
                results[symbol] = df
        except Exception as e:
            print(f"❌ {symbol}: 下载失败 - {e}")

        # 进度显示
        if i % 10 == 0 or i == total:
            print(f"   进度: {i}/{total}")

        # 限速
        if i < total:
            time.sleep(delay)

    print("-" * 50)
    print(f"📦 下载完成: 成功 {len(results)}/{total}")
    return results


def load_csv(symbol: str) -> pd.DataFrame:
    """
    从本地 CSV 加载已下载的股票数据

    参数
    ----
    symbol : 股票代码

    返回
    ----
    pd.DataFrame
    """
    filename = f"{symbol.replace('.', '_')}.csv"
    path = config.DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"找不到 {symbol} 的数据文件: {path}\n"
            f"请先运行 fetch_and_save('{symbol}') 下载数据"
        )
    df = pd.read_csv(path)
    # 尝试解析日期列
    for date_col in ["trade_date", "date"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
            break
    return df


# ==================== 快速测试 ====================
if __name__ == "__main__":
    # 测试单只下载
    test_symbol = "600519.SH"  # 贵州茅台
    path = fetch_and_save(test_symbol)
    if path:
        print(f"\n文件已保存: {path}")
        df = pd.read_csv(path)
        print(f"数据预览:\n{df.head()}")
        print(f"数据行数: {len(df)}")

