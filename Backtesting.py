import backtrader as bt
from datetime import datetime
import yfinance as yf  # For data download

def run_orb_backtest():
    """Complete backtesting setup with optimization"""
    cerebro = bt.Cerebro()
    
    # Import the strategy from the other file
    from Core_Strategy_Structure import PortfolioORBStrategy
    
    # Add strategy
    cerebro.addstrategy(
        PortfolioORBStrategy,
        num_opening_bars=3,
        max_positions=5,
        volume_threshold=1.5,
        ma_period=50,
        use_ma_filter=True
    )
    
    # Add multiple data feeds
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']
    
    for symbol in symbols:
        # Download data using yfinance instead of YahooFinanceData
        df = yf.download(symbol, start='2020-01-01', end='2024-01-01', interval='1d')
        
        # Create a backtrader data feed
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,
            open=0,
            high=1,
            low=2,
            close=3,
            volume=4,
            openinterest=-1
        )
        
        cerebro.adddata(data, name=symbol)
    
    # Broker settings
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    
    # Run backtest
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # Extract performance metrics
    strat = results[0]
    
    # Sharpe Ratio
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe_analysis.get('sharperatio', 0)
    
    # Drawdown
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown_analysis.get('max', {}).get('drawdown', 0)
    
    # Returns
    returns_analysis = strat.analyzers.returns.get_analysis()
    total_return = returns_analysis.get('rtot', 0)
    annual_return = returns_analysis.get('rnorm', 0)
    
    # Trade Analysis
    trade_analysis = strat.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('total', 0)
    winning_trades = trade_analysis.get('won', {}).get('total', 0)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Print results
    print(f"\n=== BACKTEST RESULTS ===")
    print(f"Total Return: {total_return:.2%}")
    print(f"Annual Return: {annual_return:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Maximum Drawdown: {max_drawdown:.2%}")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    
    return results

# Parameter optimization function
def optimize_orb_parameters():
    """Optimize ORB strategy parameters"""
    cerebro = bt.Cerebro(optreturn=False)
    
    from Core_Strategy_Structure import OpeningRangeBreakout
    
    # Download SPY data
    df = yf.download('SPY', start='2020-01-01', end='2023-01-01', interval='1d')
    
    # Add data
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open=0,
        high=1,
        low=2,
        close=3,
        volume=4,
        openinterest=-1
    )
    cerebro.adddata(data)
    
    # Optimization strategy
    cerebro.optstrategy(
        OpeningRangeBreakout,
        num_opening_bars=range(2, 6),          # Test 2-5 bars
        volume_threshold=[1.2, 1.5, 2.0],     # Volume thresholds
        stop_atr_multiple=[1.5, 2.0, 2.5],    # Stop distances
        profit_atr_multiple=[2.0, 3.0, 4.0]   # Profit targets
    )
    
    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    # Run optimization
    results = cerebro.run(maxcpus=4)
    
    # Process results
    optimization_results = []
    for result in results:
        strat = result[0]
        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        returns = strat.analyzers.returns.get_analysis().get('rtot', 0)
        
        optimization_results.append({
            'opening_bars': strat.params.num_opening_bars,
            'volume_threshold': strat.params.volume_threshold,
            'stop_multiple': strat.params.stop_atr_multiple,
            'profit_multiple': strat.params.profit_atr_multiple,
            'sharpe_ratio': sharpe,
            'total_return': returns
        })
    
    # Sort by Sharpe ratio
    optimization_results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    
    print("\n=== TOP 5 PARAMETER COMBINATIONS ===")
    for i, result in enumerate(optimization_results[:5], 1):
        print(f"{i}. Opening Bars: {result['opening_bars']}, "
              f"Volume: {result['volume_threshold']}, "
              f"Stop: {result['stop_multiple']}, "
              f"Target: {result['profit_multiple']}")
        print(f"   Sharpe: {result['sharpe_ratio']:.2f}, "
              f"Return: {result['total_return']:.2%}\n")
    
    return optimization_results

# Usage example
if __name__ == "__main__":
    # Run basic backtest
    results = run_orb_backtest()
    
    # Run parameter optimization
    # opt_results = optimize_orb_parameters()  # Uncomment to run optimization