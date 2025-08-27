import backtrader as bt
from datetime import datetime, time

class OpeningRangeBreakout(bt.Strategy):
    params = dict(
        num_opening_bars=3,      # 15-minute ORB with 5-min bars
        volume_threshold=1.5,    # 150% volume confirmation
        atr_period=14,          # ATR for position sizing
        stop_atr_multiple=2.0,  # Stop loss distance
        profit_atr_multiple=3.0, # Profit target distance
        max_risk_per_trade=0.02  # 2% risk per trade
    )
    
    def __init__(self):
        # Opening range tracking
        self.opening_range_high = {}
        self.opening_range_low = {}
        self.range_set = {}
        
        # Indicators for each data feed
        self.volume_ma = {}
        self.atr = {}
        
        for data in self.datas:
            self.opening_range_high[data] = 0
            self.opening_range_low[data] = float('inf')
            self.range_set[data] = False
            
            # Volume and volatility indicators
            self.volume_ma[data] = bt.indicators.SMA(
                data.volume, period=20
            )
            self.atr[data] = bt.indicators.ATR(
                data, period=self.params.atr_period
            )
        
        # Order management
        self.orders = {}
        self.stop_orders = {}
        self.target_orders = {}
    
    def next(self):
        for data in self.datas:
            self.process_data(data)
    
    def process_data(self, data):
        # Set opening range during first N bars
        if len(data) <= self.params.num_opening_bars:
            self.opening_range_high[data] = max(
                self.opening_range_high[data], data.high[0]
            )
            self.opening_range_low[data] = min(
                self.opening_range_low[data], data.low[0]
            )
            return
        
        # Mark range as set after opening period
        if not self.range_set[data]:
            self.range_set[data] = True
        
        # Skip if pending orders
        if data in self.orders and self.orders[data]:
            return
        
        position = self.getposition(data)
        
        # Exit logic with stops and targets
        if position.size:
            self.manage_position(data, position)
            return
        
        # Entry logic with volume confirmation
        self.check_entry_signals(data)
    
    def check_entry_signals(self, data):
        # Volume confirmation
        volume_confirmed = (
            data.volume[0] > 
            self.volume_ma[data][0] * self.params.volume_threshold
        )
        
        if not volume_confirmed:
            return
        
        # Long entry on upward breakout
        if data.close[0] > self.opening_range_high[data]:
            size = self.calculate_position_size(data, True)
            if size > 0:
                self.orders[data] = self.buy(data=data, size=size)
                self.set_stop_and_target(data, True, data.close[0])
        
        # Short entry on downward breakout  
        elif data.close[0] < self.opening_range_low[data]:
            size = self.calculate_position_size(data, False)
            if size > 0:
                self.orders[data] = self.sell(data=data, size=size)
                self.set_stop_and_target(data, False, data.close[0])
    
    def calculate_position_size(self, data, is_long):
        """Risk-based position sizing using ATR"""
        account_value = self.broker.getvalue()
        risk_amount = account_value * self.params.max_risk_per_trade
        
        atr_value = self.atr[data][0]
        stop_distance = atr_value * self.params.stop_atr_multiple
        
        if stop_distance > 0:
            shares = int(risk_amount / stop_distance)
            return max(shares, 1)
        return 1
    
    def set_stop_and_target(self, data, is_long, entry_price):
        """Set stop loss and profit target orders"""
        atr_value = self.atr[data][0]
        
        if is_long:
            stop_price = entry_price - (atr_value * self.params.stop_atr_multiple)
            target_price = entry_price + (atr_value * self.params.profit_atr_multiple)
        else:
            stop_price = entry_price + (atr_value * self.params.stop_atr_multiple)
            target_price = entry_price - (atr_value * self.params.profit_atr_multiple)
        
        # Store for manual management (backtrader bracket orders can be complex)
        self.stop_orders[data] = stop_price
        self.target_orders[data] = target_price
    
    def manage_position(self, data, position):
        """Manage existing positions with stops and targets"""
        if position.size > 0:  # Long position
            if (data.low[0] <= self.stop_orders[data] or 
                data.high[0] >= self.target_orders[data]):
                self.close(data=data)
        
        elif position.size < 0:  # Short position
            if (data.high[0] >= self.stop_orders[data] or 
                data.low[0] <= self.target_orders[data]):
                self.close(data=data)
    
    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            # Clear order reference
            for data in self.datas:
                if self.orders.get(data) == order:
                    self.orders[data] = None
                    break


# Enhanced multi-data portfolio implementation
class PortfolioORBStrategy(bt.Strategy):
    params = dict(
        num_opening_bars=3,
        max_positions=5,
        volume_threshold=1.5,
        ma_period=50,
        use_ma_filter=True
    )
    
    def __init__(self):
        self.opening_ranges = {}
        self.indicators = {}
        self.orders = {}
        
        # Setup indicators for each data feed
        for data in self.datas:
            self.opening_ranges[data] = {
                'high': 0, 'low': float('inf'), 'set': False
            }
            self.orders[data] = None
            
            # Technical indicators
            self.indicators[data] = {
                'volume_ma': bt.indicators.SMA(data.volume, period=20),
                'price_ma': bt.indicators.SMA(data.close, period=self.params.ma_period),
                'atr': bt.indicators.ATR(data, period=14)
            }
    
    def next(self):
        current_positions = sum(1 for d in self.datas if self.getposition(d).size != 0)
        
        for data in self.datas:
            self.process_portfolio_data(data, current_positions)
    
    def process_portfolio_data(self, data, current_positions):
        # Set opening range
        if len(data) <= self.params.num_opening_bars:
            self.opening_ranges[data]['high'] = max(
                self.opening_ranges[data]['high'], data.high[0]
            )
            self.opening_ranges[data]['low'] = min(
                self.opening_ranges[data]['low'], data.low[0]
            )
            return
        
        self.opening_ranges[data]['set'] = True
        
        # Skip if max positions reached or pending order
        if (current_positions >= self.params.max_positions or 
            self.orders[data]):
            return
        
        position = self.getposition(data)
        
        if not position.size:
            self.check_portfolio_entry(data)
    
    def check_portfolio_entry(self, data):
        # Volume confirmation
        volume_confirmed = (
            data.volume[0] > 
            self.indicators[data]['volume_ma'][0] * self.params.volume_threshold
        )
        
        if not volume_confirmed:
            return
        
        # Moving average filter
        if self.params.use_ma_filter:
            price_ma = self.indicators[data]['price_ma'][0]
            
            # Long entry: above opening range high AND above MA
            if (data.close[0] > self.opening_ranges[data]['high'] and 
                data.close[0] > price_ma):
                size = self.calculate_portfolio_size(data)
                self.orders[data] = self.buy(data=data, size=size)
            
            # Short entry: below opening range low AND below MA
            elif (data.close[0] < self.opening_ranges[data]['low'] and 
                  data.close[0] < price_ma):
                size = self.calculate_portfolio_size(data)
                self.orders[data] = self.sell(data=data, size=size)
        
        else:
            # No MA filter - trade both directions
            if data.close[0] > self.opening_ranges[data]['high']:
                size = self.calculate_portfolio_size(data)
                self.orders[data] = self.buy(data=data, size=size)
            elif data.close[0] < self.opening_ranges[data]['low']:
                size = self.calculate_portfolio_size(data)
                self.orders[data] = self.sell(data=data, size=size)
    
    def calculate_portfolio_size(self, data):
        """Portfolio-level position sizing"""
        account_value = self.broker.getvalue()
        
        # Risk 1% per position with max 5 positions = 5% total portfolio risk
        risk_per_position = account_value * 0.01
        
        atr_value = self.indicators[data]['atr'][0]
        stop_distance = atr_value * 2.0
        
        if stop_distance > 0:
            shares = int(risk_per_position / stop_distance)
            return max(shares, 1)
        return 1