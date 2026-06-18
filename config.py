"""
全局配置
敏感信息（API_KEY）从 .env 加载，不提交到 Git
非敏感配置（路径、参数）放在这里，提交到 Git
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ==================== 路径配置 ====================
# 项目根目录（config.py 所在目录）
PROJECT_ROOT = Path(__file__).parent

# CSV 数据存放目录
DATA_DIR = PROJECT_ROOT / "datasets"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# ==================== API 配置 ====================
load_dotenv(PROJECT_ROOT / ".env")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("请在 .env 文件中设置 API_KEY")

# ==================== 回测参数 ====================
BACKTEST = {
    "initial_cash": 1_000_000,       # 初始资金（元）
    "commission": 0.0003,            # 手续费率（万三）
    "stamp_tax": 0.0005,             # 印花税（万五，仅卖出时收取）
    "slippage": 0.001,               # 滑点（0.1%）
    "start_date": "2021-01-01",      # 回测起始日期
    "end_date": "2026-06-18",        # 回测结束日期
}

# ==================== 股票池配置 ====================
UNIVERSE = {
    "min_amount": 1e8,               # 最低日均成交金额（1 亿元）
    "min_market_cap": 5e9,           # 最低总市值（50亿）
    "exclude_st": True,              # 排除 ST 股票
    "exclude_new_days": 60,          # 排除上市不满60天的新股
}

# ==================== 因子配置 ====================
FACTORS = {
    "momentum_window": 252,          # 动量因子回看窗口（12个月）
    "volatility_window": 60,         # 波动率因子回看窗口（60天）
    "top_n": 10,                     # 选股数量
    "rebalance_freq": "monthly",     # 调仓频率
}
