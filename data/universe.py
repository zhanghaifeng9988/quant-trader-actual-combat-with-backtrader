"""
data/universe.py
股票池筛选模块

功能：
  - 预定义蓝筹股票池（覆盖主要行业）
  - 基于成交量、市值、ST、上市时间等条件筛选
  - 支持自定义股票列表
  - 数据质量检查由 data/quality.py 负责
"""
import sys
import time
import datetime
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config


# ==================== 预定义股票池 ====================

# 108 只股票，覆盖 A 股主要行业 + 新兴赛道（沪深两市均衡分布）
BLUE_CHIP = [
    # === 金融 ===
    "601398.SH",  # 工商银行
    "601939.SH",  # 建设银行
    "600036.SH",  # 招商银行
    "601166.SH",  # 兴业银行
    "601318.SH",  # 中国平安
    "600030.SH",  # 中信证券
    # === 食品饮料 ===
    "600519.SH",  # 贵州茅台
    "000858.SZ",  # 五粮液
    "000568.SZ",  # 泸州老窖
    "603288.SH",  # 海天味业
    "002304.SZ",  # 洋河股份
    "600887.SH",  # 伊利股份
    # === 家电/消费 ===
    "000333.SZ",  # 美的集团
    "000651.SZ",  # 格力电器
    "600690.SH",  # 海尔智家
    # === 医药 ===
    "600276.SH",  # 恒瑞医药
    "000538.SZ",  # 云南白药
    "300760.SZ",  # 迈瑞医疗
    "600196.SH",  # 复星医药
    # === 科技/电子 ===
    "002415.SZ",  # 海康威视
    "603986.SH",  # 兆易创新
    "002371.SZ",  # 北方华创
    "688981.SH",  # 中芯国际
    # === 新能源 ===
    "300750.SZ",  # 宁德时代
    "002594.SZ",  # 比亚迪
    "601012.SH",  # 隆基绿能
    "300274.SZ",  # 阳光电源
    # === 通信/计算机 ===
    "000063.SZ",  # 中兴通讯
    "600588.SH",  # 用友网络
    "002230.SZ",  # 科大讯飞
    # === 交通运输 ===
    "601006.SH",  # 大秦铁路
    "600029.SH",  # 南方航空
    "601111.SH",  # 中国国航
    "600115.SH",  # 中国东航
    # === 能源/材料 ===
    "601857.SH",  # 中国石油
    "600028.SH",  # 中国石化
    "601088.SH",  # 中国神华
    "600585.SH",  # 海螺水泥
    "600309.SH",  # 万华化学
    "002460.SZ",  # 赣锋锂业
    # === 制造/工业 ===
    "600031.SH",  # 三一重工
    "002008.SZ",  # 大族激光
    "601668.SH",  # 中国建筑
    # === 电信/公用事业 ===
    "600941.SH",  # 中国移动
    "601728.SH",  # 中国电信
    # === 房地产 ===
    "001979.SZ",  # 招商蛇口
    "000002.SZ",  # 万科A
    # === 农业 ===
    "300498.SZ",  # 温氏股份
    "002714.SZ",  # 牧原股份
    # === AI / 人工智能 ===
    "688256.SH",  # 寒武纪（AI 芯片）
    "688111.SH",  # 金山办公（AI + 办公软件）
    "603019.SH",  # 中科曙光（AI 算力服务器）
    "688787.SH",  # 海天瑞声（AI 训练数据）
    "002236.SZ",  # 大华股份（AI 视觉）
    "688041.SH",  # 海光信息（国产 GPU/CPU）
    "601138.SH",  # 工业富联（AI 服务器代工）
    "002281.SZ",  # 光迅科技（光模块）
    "300308.SZ",  # 中际旭创（光模块龙头）
    "300502.SZ",  # 新易盛（光模块）
    "300394.SZ",  # 天孚通信（光器件）
    "300475.SZ",  # 香农芯创（芯片分销）
    "001309.SZ",  # 德明利（存储模组）
    "002384.SZ",  # 东山精密（FPC/光模块）
    # === 机器人 ===
    "300124.SZ",  # 汇川技术（工业机器人伺服）
    "300024.SZ",  # 机器人（新松，机器人本体）
    "688169.SH",  # 石头科技（扫地机器人）
    "002747.SZ",  # 埃斯顿（工业机器人）
    # === 航空航天 / 军工 ===
    "600760.SH",  # 中航沈飞（歼击机）
    "601989.SH",  # 中国重工（舰船）
    "600893.SH",  # 航发动力（航空发动机）
    "600150.SH",  # 中国船舶（造船）
    "002179.SZ",  # 中航光电（军工连接器）
    # === 碳减排 / 清洁能源 ===
    "601865.SH",  # 福莱特（光伏玻璃）
    "002129.SZ",  # 中环股份 / TCL中环（硅片）
    "600438.SH",  # 通威股份（光伏 + 硅料）
    "002202.SZ",  # 金风科技（风电整机）
    "300450.SZ",  # 先导智能（锂电设备）
    # === 综合龙头补充 ===
    "000725.SZ",  # 京东方A（显示面板龙头）
    "601899.SH",  # 紫金矿业（黄金/铜矿龙头）
    "000100.SZ",  # TCL科技（面板 + 半导体）
    "600176.SH",  # 中国巨石（玻纤龙头）
    "300570.SZ",  # 太辰光（光器件）
    "300088.SZ",  # 长信科技（触控显示）
    "600110.SH",  # 诺德股份（铜箔）
    "002600.SZ",  # 领益制造（精密结构件）
    "300418.SZ",  # 昆仑万维（AI 大模型/游戏）
    "600392.SH",  # 盛和资源（稀土）
    # === 互联网 / 软件 ===
    "300059.SZ",  # 东方财富（互联网金融）
    "300033.SZ",  # 同花顺（金融 IT）
    "601360.SH",  # 三六零（安全 + AI）
    "002027.SZ",  # 分众传媒（广告龙头）
    "002555.SZ",  # 三七互娱（游戏）
    # === 矿业 / 资源 ===
    "600111.SH",  # 北方稀土（稀土龙头）
    "603993.SH",  # 洛阳钼业（钴/钼/铜）
    "600362.SH",  # 江西铜业（铜业龙头）
    # === 钢铁 ===
    "600019.SH",  # 宝钢股份（钢铁龙头）
    "000898.SZ",  # 鞍钢股份
    # === 化工 ===
    "000301.SZ",  # 东方盛虹（炼化一体化）
    "600346.SH",  # 恒力石化（民营炼化）
    "600426.SH",  # 华鲁恒升（煤化工龙头）
    # === 交通运输补充 ===
    "002352.SZ",  # 顺丰控股（快递龙头）
    "601919.SH",  # 中远海控（集装箱航运）
    "600009.SH",  # 上海机场（机场龙头）
    # === 农畜牧补充 ===
    "000876.SZ",  # 新希望（饲料 + 养猪）
    "603345.SH",  # 安井食品（速冻食品龙头）
    "002311.SZ",  # 海大集团（水产饲料龙头）
    "603501.SH",  # 韦尔股份（半导体 CIS）
]


def get_blue_chip_symbols(n: int = 108) -> list[str]:
    """
    获取蓝筹股票池

    参数
    ----
    n : 需要多少只股票（最多 108）

    返回
    ----
    股票代码列表
    """
    return BLUE_CHIP[:n]


def load_from_csv(filepath: str) -> list[str]:
    """
    从 CSV 文件加载股票列表

    CSV 格式要求：至少有一列名为 'symbol' 或 '股票代码'

    参数
    ----
    filepath : CSV 文件路径

    返回
    ----
    股票代码列表
    """
    df = pd.read_csv(filepath)

    # 尝试找到股票代码列
    for col in ["symbol", "股票代码", "code", "ts_code"]:
        if col in df.columns:
            return df[col].dropna().tolist()

    raise ValueError(
        f"CSV 中找不到股票代码列。"
        f"支持的列名: symbol, 股票代码, code, ts_code\n"
        f"当前列名: {list(df.columns)}"
    )


def filter_by_amount(
    symbols: list[str],
    min_avg_amount: float = None,
    lookback_days: int = 20,
    keep_symbols: list[str] = None,
) -> list[str]:
    """
    基于近期成交金额筛选：剔除日均成交金额过低的股票

    参数
    ----
    symbols        : 候选股票代码列表
    min_avg_amount : 最低日均成交金额（元），默认取 config.UNIVERSE['min_amount']
    lookback_days  : 回看天数
    keep_symbols   : 强制保留的股票列表（成交金额不达标也保留）

    返回
    ----
    筛选后的股票代码列表
    """
    if min_avg_amount is None:
        min_avg_amount = config.UNIVERSE["min_amount"]

    if keep_symbols is None:
        keep_symbols = []

    from data.fetcher import load_csv

    passed = []
    print(f"🔍 成交金额筛选（最近 {lookback_days} 天，"
          f"日均成交金额 > {min_avg_amount/1e8:.1f} 亿元）")

    for symbol in symbols:
        # 强制保留的特例
        if symbol in keep_symbols:
            print(f"  ℹ️  {symbol}: 特例保留（成交金额不达标也保留）")
            passed.append(symbol)
            continue

        try:
            df = load_csv(symbol)
            if len(df) < lookback_days:
                print(f"  ⚠️  {symbol}: 数据不足 {lookback_days} 天，跳过")
                continue

            recent = df.tail(lookback_days)
            avg_amount = recent["amount"].mean()

            if avg_amount >= min_avg_amount:
                passed.append(symbol)
            else:
                print(f"  ❌ {symbol}: 日均成交金额 {avg_amount/1e8:.2f} 亿 < "
                      f"{min_avg_amount/1e8:.1f} 亿，剔除")
        except FileNotFoundError:
            print(f"  ⚠️  {symbol}: 无本地数据，跳过")

    print(f"✅ 成交金额筛选完成: {len(passed)}/{len(symbols)} 只通过")
    return passed


# ==================== tickflow 基础信息获取 ====================

def _fetch_instruments(symbols: list[str], delay: float = 0.5) -> dict:
    """
    批量获取股票基础信息（用 free 服务，不消耗 K 线配额）

    参数
    ----
    symbols : 股票代码列表
    delay   : 每次请求间隔（秒），避免限流

    返回
    ----
    dict: {symbol: instrument_dict}
    """
    from tickflow import TickFlow
    tf = TickFlow.free()

    results = {}
    print(f"🔍 批量获取 {len(symbols)} 只股票基础信息...")

    for i, symbol in enumerate(symbols):
        try:
            info = tf.instruments.get(symbol)
            results[symbol] = info
            if (i + 1) % 20 == 0:
                print(f"  ... 已获取 {i + 1}/{len(symbols)}")
            time.sleep(delay)
        except Exception as e:
            print(f"  ⚠️  {symbol}: 获取失败 ({e})")

    print(f"✅ 基础信息获取: {len(results)}/{len(symbols)} 只成功")
    return results


# ==================== ST 过滤 ====================

def filter_by_st(
    symbols: list[str],
    instruments: dict = None,
) -> list[str]:
    """
    剔除 ST / *ST 股票（name 中包含 "ST" 字样）

    参数
    ----
    symbols     : 候选股票代码列表
    instruments : 已获取的基础信息 dict（可选，不提供则自动获取）

    返回
    ----
    筛选后的股票代码列表
    """
    if instruments is None:
        instruments = _fetch_instruments(symbols)

    passed = []
    print(f"🔍 ST 过滤（剔除名称含 ST 的股票）")

    for symbol in symbols:
        info = instruments.get(symbol)
        if info is None:
            print(f"  ⚠️  {symbol}: 无基础信息，保留")
            passed.append(symbol)
            continue

        name = info.get("name", "")
        if "ST" in name.upper():
            print(f"  ❌ {symbol} {name}: ST 股票，剔除")
        else:
            passed.append(symbol)

    print(f"✅ ST 过滤完成: {len(passed)}/{len(symbols)} 只通过")
    return passed


# ==================== 市值过滤 ====================

def filter_by_market_cap(
    symbols: list[str],
    min_market_cap: float = None,
    instruments: dict = None,
    keep_symbols: list[str] = None,
) -> list[str]:
    """
    剔除总市值过低的股票（total_shares × 最近收盘价）

    参数
    ----
    symbols        : 候选股票代码列表
    min_market_cap : 最低总市值（元），默认取 config.UNIVERSE['min_market_cap']
    instruments    : 已获取的基础信息 dict（可选）
    keep_symbols   : 强制保留的股票列表（市值不达标也保留）

    返回
    ----
    筛选后的股票代码列表
    """
    if min_market_cap is None:
        min_market_cap = config.UNIVERSE["min_market_cap"]

    if keep_symbols is None:
        keep_symbols = []

    if instruments is None:
        instruments = _fetch_instruments(symbols)

    from data.fetcher import load_csv

    passed = []
    print(f"🔍 市值筛选（总市值 > {min_market_cap/1e8:.0f} 亿）")

    for symbol in symbols:
        # 强制保留的特例
        if symbol in keep_symbols:
            print(f"  ℹ️  {symbol}: 特例保留（市值不达标也保留）")
            passed.append(symbol)
            continue
        info = instruments.get(symbol)
        if info is None:
            print(f"  ⚠️  {symbol}: 无基础信息，保留")
            passed.append(symbol)
            continue

        ext = info.get("ext", {})
        total_shares = ext.get("total_shares")

        if total_shares is None or total_shares <= 0:
            print(f"  ⚠️  {symbol}: 无总股本数据，保留")
            passed.append(symbol)
            continue

        # 从本地 CSV 取最近收盘价
        try:
            df = load_csv(symbol)
            latest_close = df["close"].iloc[-1]
        except (FileNotFoundError, KeyError, IndexError):
            print(f"  ⚠️  {symbol}: 无收盘价数据，保留")
            passed.append(symbol)
            continue

        market_cap = total_shares * latest_close
        market_cap_yi = market_cap / 1e8  # 换算成亿

        if market_cap >= min_market_cap:
            passed.append(symbol)
        else:
            print(f"  ❌ {symbol}: 总市值 {market_cap_yi:.1f} 亿 < "
                  f"{min_market_cap/1e8:.0f} 亿，剔除")

    print(f"✅ 市值筛选完成: {len(passed)}/{len(symbols)} 只通过")
    return passed


# ==================== 新股过滤 ====================

def filter_by_listing_date(
    symbols: list[str],
    min_days: int = None,
    instruments: dict = None,
) -> list[str]:
    """
    剔除上市不满 N 天的新股（数据不够回测用）

    参数
    ----
    symbols     : 候选股票代码列表
    min_days    : 最低上市天数，默认取 config.UNIVERSE['exclude_new_days']
    instruments : 已获取的基础信息 dict（可选）

    返回
    ----
    筛选后的股票代码列表
    """
    if min_days is None:
        min_days = config.UNIVERSE["exclude_new_days"]

    if instruments is None:
        instruments = _fetch_instruments(symbols)

    passed = []
    today = datetime.date.today()
    print(f"🔍 新股过滤（上市满 {min_days} 天）")

    for symbol in symbols:
        info = instruments.get(symbol)
        if info is None:
            print(f"  ⚠️  {symbol}: 无基础信息，保留")
            passed.append(symbol)
            continue

        ext = info.get("ext", {})
        listing_date_str = ext.get("listing_date")

        if listing_date_str is None:
            print(f"  ⚠️  {symbol}: 无上市日期数据，保留")
            passed.append(symbol)
            continue

        listing_date = datetime.datetime.strptime(listing_date_str, "%Y-%m-%d").date()
        days_listed = (today - listing_date).days

        if days_listed >= min_days:
            passed.append(symbol)
        else:
            print(f"  ❌ {symbol}: 上市仅 {days_listed} 天 < "
                  f"{min_days} 天，剔除")

    print(f"✅ 新股过滤完成: {len(passed)}/{len(symbols)} 只通过")
    return passed


def get_universe(
    symbols: list[str] = None,
    n: int = 110,
    apply_st_filter: bool = True,
    apply_market_cap_filter: bool = True,
    apply_listing_date_filter: bool = True,
    apply_volume_filter: bool = True,
    apply_quality_filter: bool = True,
    market_cap_keep: list[str] = None,
    amount_keep: list[str] = None,
) -> list[str]:
    """
    获取最终股票池（一站式调用，按顺序执行全部筛选）

    筛选流程：
      ① ST 过滤       → 剔除 ST/*ST 股票
      ② 新股过滤       → 剔除上市不满 N 天的新股
      ③ 市值过滤       → 剔除总市值 < 50 亿的（可指定特例保留）
      ④ 成交金额筛选   → 剔除日均成交金额 < 1 亿的（可指定特例保留）
      ⑤ 数据质量检查   → 空值填充、标记待人工确认

    参数
    ----
    symbols                  : 自定义股票列表，默认使用蓝筹股票池
    n                        : 如果使用默认列表，取前 n 只
    apply_st_filter          : 是否过滤 ST 股票
    apply_market_cap_filter  : 是否过滤低市值股票
    apply_listing_date_filter: 是否过滤新股
    apply_volume_filter      : 是否应用成交金额筛选
    apply_quality_filter     : 是否应用数据完整性检查
    market_cap_keep          : 市值过滤时强制保留的股票列表
    amount_keep              : 成交金额过滤时强制保留的股票列表

    返回
    ----
    筛选后的股票代码列表
    """
    # 第 0 步：确定候选池
    if symbols is None:
        symbols = get_blue_chip_symbols(n)

    print(f"=" * 60)
    print(f"📋 股票池筛选")
    print(f"   候选股票数: {len(symbols)}")
    print(f"=" * 60)

    # 批量获取基础信息（ST/市值/新股 三个过滤器共用，只请求一次）
    need_instruments = apply_st_filter or apply_market_cap_filter or apply_listing_date_filter
    instruments = {}
    if need_instruments:
        instruments = _fetch_instruments(symbols)

    # 第 1 步：ST 过滤
    if apply_st_filter:
        symbols = filter_by_st(symbols, instruments=instruments)

    # 第 2 步：新股过滤
    if apply_listing_date_filter:
        symbols = filter_by_listing_date(symbols, instruments=instruments)

    # 第 3 步：市值过滤（可指定特例保留）
    if market_cap_keep is None:
        market_cap_keep = []  # 无特例
    if apply_market_cap_filter:
        symbols = filter_by_market_cap(symbols, instruments=instruments, keep_symbols=market_cap_keep)

    # 第 4 步：成交金额筛选（可指定特例保留）
    if amount_keep is None:
        amount_keep = ["000898.SZ"]  # 鞍钢股份：成交金额不达标但保留
    if apply_volume_filter:
        symbols = filter_by_amount(symbols, keep_symbols=amount_keep)

    # 第 5 步：数据完整性检查（不删除，只标记和填充）
    if apply_quality_filter:
        from data.quality import check_data_quality
        symbols, need_review, report = check_data_quality(symbols)

    print(f"=" * 60)
    print(f"📋 最终股票池: {len(symbols)} 只")
    print(f"=" * 60)

    return symbols


# ==================== 快速测试 ====================
if __name__ == "__main__":
    # 测试：打印蓝筹股列表
    symbols = get_blue_chip_symbols(10)
    print(f"蓝筹股前 10 只: {symbols}")
    print()

    # 测试：完整筛选流程（需要先下载数据）
    # universe = get_universe(n=10)
    # print(f"\n最终股票池: {universe}")
