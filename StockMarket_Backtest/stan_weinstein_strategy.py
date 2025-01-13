import backtrader as bt
import yfinance as yf

class StanWeinstein(bt.Strategy):
    params = (
        ('maperiod', 30),  # Period for the moving average
        ('rsperiod', 14),   # Period for relative strength
        ('overbought_rsi', 70),  # RSI level considered overbought
        ('oversold_rsi', 30),   # RSI level considered oversold
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        self.rsi = bt.indicators.RSI_SMA(self.datas[0].close, period=self.params.rsperiod)

        # To keep track of the current stage
        self.stage = 0  

    def next(self):
        # Stage 1: Basing (price above MA, consolidating)
        if self.stage == 0 and self.dataclose[0] > self.ma[0] and self.rsi[0] < self.params.overbought_rsi: 
            self.stage = 1  # Move to Stage 1

        # Stage 2: Advancing (price above MA, strong uptrend)
        elif self.stage == 1 and self.dataclose[0] > self.ma[0] and self.rsi[0] > self.params.oversold_rsi:
            self.buy()
            self.stage = 2  # Move to Stage 2

        # Stage 3: Topping (price below MA, or breaking down)
        elif self.stage == 2 and (self.dataclose[0] < self.ma[0] or self.rsi[0] > self.params.overbought_rsi):
            self.sell()
            self.stage = 3  # Move to Stage 3

        # Stage 4: Declining (price below MA, downtrend)
        elif self.stage == 3 and self.dataclose[0] < self.ma[0]:
            self.stage = 4  # Move to Stage 4

        # Reset to Stage 0 if price crosses back above MA in Stage 4
        elif self.stage == 4 and self.dataclose[0] > self.ma[0]:
            self.stage = 0  # Reset to Stage 0


if __name__ == '__main__':
    # Load data
    data = yf.download("BBCA.JK", start="2020-01-01", end="2023-12-31") 

    # Create a Cerebro engine
    cerebro = bt.Cerebro()

    # Add the data
    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)

    # Add the strategy
    cerebro.addstrategy(StanWeinstein)

    # Set initial cash
    cerebro.broker.setcash(100000.0)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # Run the backtest
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Print analyzers results
    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.sharpe.get_analysis()['sharperatio'])
    print('Max Drawdown:', strat.analyzers.drawdown.get_analysis()['max']['drawdown'])

    # Plot the results (optional)
    cerebro.plot()