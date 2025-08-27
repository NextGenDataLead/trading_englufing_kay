# Multi-Timeframe Engulfing Box Tracker

A sophisticated Pine Script v5 indicator for TradingView that identifies bullish and bearish engulfing candlestick patterns across multiple timeframes and creates interactive boxes that track price interaction.

## 🎯 Key Features

### Pattern Detection
- **Bullish & Bearish Engulfing**: Accurate detection of classic engulfing candlestick patterns
- **Multi-Timeframe Analysis**: Simultaneously monitor 4 configurable timeframes (default: 15m, 1H, 4H, 1D)
- **Advanced Filtering**: Volume confirmation, trend alignment, and minimum engulfing percentage filters
- **Non-Repainting**: Reliable signals that don't change after bar close

### Box Management System
- **Dynamic Box Creation**: Automatically creates boxes at engulfing candle high/low points
- **Lifecycle Tracking**: Boxes remain active until price touches them again
- **Multiple Active Boxes**: Supports up to 200 simultaneous boxes across all timeframes
- **State Management**: Visual feedback shows box status (Active vs Touched)

### Visual Features
- **Color-Coded Timeframes**: Each timeframe has distinct border colors for easy identification
- **Smart Labels**: Optional labels showing timeframe and pattern type
- **Touch Indicators**: Clear visual feedback when price interacts with boxes
- **Customizable Styling**: Full control over colors, border width, and transparency

## 🚀 How It Works

1. **Pattern Detection**: Script continuously scans each enabled timeframe for engulfing patterns
2. **Box Creation**: When a pattern is detected, a box is created spanning the candle's high/low range
3. **Extension**: Active boxes extend forward in time until price touches them
4. **Touch Event**: When price intersects a box, it changes color and stops being considered "active"
5. **Multi-Box Support**: Multiple boxes can be active simultaneously, each tracked independently

## ⚙️ Configuration Options

### Timeframes
- **4 Configurable Timeframes**: Set any timeframe for each slot
- **Individual Enable/Disable**: Toggle each timeframe on/off independently
- **Current Timeframe**: Also monitors the chart's current timeframe

### Pattern Filters
- **Volume Filter**: Require higher volume than previous bar
- **Trend Filter**: Only show patterns aligned with EMA trend direction  
- **Min Engulfing %**: Set minimum percentage the current candle must engulf
- **EMA Period**: Configurable moving average for trend determination

### Box Settings
- **Extension Length**: How many bars to initially extend boxes
- **Border Width**: Customizable border thickness (1-5 pixels)
- **Show Labels**: Toggle pattern and touch labels on/off

### Colors & Styling
- **Bullish/Bearish Colors**: Separate colors for bull/bear patterns
- **Touched Color**: Distinct color when boxes are no longer active
- **Timeframe Borders**: Unique border color for each timeframe
- **Transparency**: Adjustable background opacity

## 📊 Usage Examples

### Swing Trading
- Use higher timeframes (4H, 1D) for major swing points
- Look for confluence when multiple timeframes show patterns
- Wait for box touches as potential entry/exit signals

### Scalping
- Focus on lower timeframes (5m, 15m) for quick reversals
- Use volume filter to confirm pattern strength
- Monitor current timeframe boxes for immediate opportunities

### Multi-Timeframe Analysis
- Enable all timeframes for comprehensive market view
- Look for pattern alignment across timeframes
- Use box touches to time entries with higher probability

## 🔧 Installation & Setup

1. **Copy the Pine Script**: Copy the contents of `engulfing_box_tracker.pine`
2. **Add to TradingView**: Paste into Pine Script editor
3. **Configure Settings**: Adjust timeframes and filters to your preference
4. **Apply to Chart**: Add the indicator to your chart
5. **Customize Appearance**: Set colors and styling to match your setup

## 📋 Best Practices

### Pattern Recognition
- Combine with other technical analysis for confirmation
- Pay attention to volume during engulfing patterns
- Consider market context (support/resistance levels)

### Box Management
- Monitor multiple active boxes for confluence zones
- Use touched boxes as potential support/resistance levels
- Be aware of box density - too many overlapping boxes can be confusing

### Performance Optimization
- Disable unused timeframes to improve performance
- Use appropriate chart timeframe for your analysis style
- Consider box extension length based on your trading horizon

## 🚨 Alerts & Notifications

The script includes alert conditions for:
- Any engulfing pattern detection
- Specific bullish engulfing patterns
- Specific bearish engulfing patterns

Set up TradingView alerts to get notified of new patterns in real-time.

## 🔍 Technical Details

### Pine Script Version
- Built with Pine Script v5
- Compatible with all TradingView account types
- Maximum 200 boxes supported (Pine Script limitation)

### Performance Considerations
- Optimized `request.security()` calls using tuples
- Efficient array-based box management
- Backward iteration for optimal performance
- Memory cleanup for touched boxes

### Non-Repainting Design
- Uses `lookahead=barmerge.lookahead_on` for consistent signals
- Historical and real-time behavior is identical
- Patterns confirm only after bar close

## 📁 Project Structure

```
Trading/
├── engulfing_box_tracker.pine          # Main Pine Script file
├── .claude/
│   ├── PLAN.md                         # Comprehensive implementation plan
│   ├── tasks/TODO_ENGULFING_BOX_TRACKER.md  # Detailed task breakdown
│   └── tests/TEST_ENGULFING_BOX_TRACKER.md  # Testing strategy
└── README.md                           # This file
```

## 🧪 Testing

Comprehensive testing documentation is available in `.claude/tests/TEST_ENGULFING_BOX_TRACKER.md`, covering:
- Pattern detection accuracy
- Multi-timeframe synchronization
- Box lifecycle management
- Performance under load
- Edge case handling

## 🤝 Development Notes

This project was developed using advanced research tools:
- **Context7 MCP**: For Pine Script documentation and best practices
- **EXA MCP**: For deep research on implementation patterns and optimization

For future enhancements or troubleshooting, continue using these tools for the most comprehensive and up-to-date information.

## ⚡ Quick Start

1. **Default Configuration**: The script works out-of-box with sensible defaults
2. **Enable Timeframes**: Start with TF1 (15m) and TF2 (1H) enabled
3. **Monitor Patterns**: Watch for engulfing signals and box creation
4. **Observe Touch Events**: Notice when price interacts with boxes
5. **Customize**: Adjust settings based on your trading style

## 📈 Example Scenarios

### Bullish Engulfing Detection
- Previous candle: Red (bearish)
- Current candle: Green (bullish) and completely engulfs previous candle body
- Volume higher than previous bar (if filter enabled)
- Box created at current candle's high/low range

### Box Touch Event  
- Price moves away from engulfing candle
- Box extends forward in time
- Price eventually returns and touches box boundary
- Box changes to "touched" color and stops extending
- Touch label appears for confirmation

---

**Disclaimer**: This indicator is for educational and analysis purposes. Always combine with proper risk management and additional confirmation signals for trading decisions.