# quant-trader-actual-combat-with-backtrader
A practical record based on the backtrader backtesting framework, starting from the Chinese A-share market
# quant-trader-actual-combat-with-backtrader

基于 Backtrader 回测框架的 A 股量化策略实战项目。

## 项目目标

用 Python + Backtrader 搭建一套完整的 A 股量化投资工作流，覆盖从数据获取到策略回测的全流程。

## 项目结构
quant-trader-actual-combat-with-backtrader/
├── data/ # 数据模块
│ ├── fetcher.py # 行情数据获取（akshare/tickflow）
│ ├── storage.py # 数据存储（Parquet + DuckDB）
│ ├── updater.py # 每日增量更新
│ └── universe.py # 股票池筛选（流动性/市值/ST过滤）
│
├── factors/ # 因子模块
│ ├── base.py # 因子基类（标准化、排名、合成）
│ ├── momentum.py # 动量因子（N日涨幅）
│ ├── volatility.py # 波动率因子（历史波动率）
│ ├── value.py # 价值因子（PE、PB、股息率）
│ └── composite.py # 多因子合成（等权/IC加权）
│
├── strategies/ # 策略模块（Backtrader Strategy）
│ ├── 01_dual_ma_trend.py # 策略1：双均线趋势跟踪
│ ├── 02_rsi_mean_reversion.py # 策略2：RSI均值回归
│ ├── 03_multi_factor_select.py # 策略3：多因子选股（月度调仓）
│ └── 04_sector_rotation.py # 策略4：行业轮动
│
├── engine/ # 回测引擎
│ ├── backtester.py # Backtrader 回测封装
│ ├── metrics.py # 绩效指标计算（Sharpe/回撤/胜率等）
│ └── report.py # 回测报告生成（图表+统计表）
│
├── portfolio/ # 组合管理
│ ├── weight.py # 权重分配（等权/Markowitz/风险平价）
│ └── risk.py # 风控规则（止损/最大持仓/回撤控制）
│
├── notebooks/ # 分析报告（Jupyter）
│ ├── 01_data_exploration.ipynb # 数据探索与可视化
│ ├── 02_factor_analysis.ipynb # 因子有效性分析（IC/分组收益）
│ ├── 03_strategy_report.ipynb # 策略回测报告
│ └── 04_comparison.ipynb # 多策略横向对比
│
├── config.py # 全局配置（API_KEY、数据路径、参数）
├── requirements.txt # 依赖清单
└── README.md # 本文件

## 实施计划

### Phase 1：数据基础（第 1 周）
- [x] 项目初始化
- [ ] 数据获取模块：akshare 拉取 A 股日线行情
- [ ] 数据存储：Parquet 格式 + DuckDB 查询
- [ ] 股票池筛选：流动性、市值、ST 过滤

### Phase 2：因子体系（第 2 周）
- [ ] 因子基类：标准化、去极值、排名打分
- [ ] 动量因子、波动率因子、价值因子
- [ ] 因子有效性验证：IC 分析、分位数收益

### Phase 3：策略开发（第 3-4 周）
- [ ] 策略1：双均线趋势跟踪
- [ ] 策略2：RSI 均值回归（穿越信号 + 止损）
- [ ] 策略3：多因子选股（月度调仓）
- [ ] 策略4：行业轮动（行业 ETF 动量排名）

### Phase 4：评估与报告（第 5 周）
- [ ] 绩效指标体系（Sharpe/Sortino/Calmar/最大回撤/胜率）
- [ ] 多策略横向对比报告
- [ ] 参数敏感性分析

## 技术栈

| 工具 | 用途 |
|------|------|
| Python 3.11 | 编程语言 |
| Backtrader | 回测框架 |
| akshare / tickflow | A 股数据获取 |
| pandas / numpy | 数据处理 |
| DuckDB | 本地分析引擎 |
| Parquet | 数据存储格式 |
| matplotlib | 可视化 |
| scipy / statsmodels | 统计分析 |

## 数据来源

- **行情数据**：tickflow（A 股日线 K 线，前复权）
- **财务数据**：akshare（PE、PB、ROE 等）
- **指数数据**：沪深 300 / 中证 500 成分股

## 运行环境

```bash
conda create -n quant-combat python=3.11
conda activate quant-combat
pip install -r requirements.txt