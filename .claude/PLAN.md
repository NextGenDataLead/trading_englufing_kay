# Pine Script Multi-Timeframe Engulfing Candle Box Tracker - Implementation Plan

## Project Overview
Create a Pine Script for TradingView that identifies engulfing candle patterns on multiple timeframes and tracks boxes with specific lifecycle management. Each box starts when an engulfing candle is detected, extends until price touches it again, then stops being considered active.

## Research Completed
- ✅ **Context7 MCP**: Researched Pine Script box drawing, multi-timeframe analysis, and candlestick patterns
- ✅ **EXA MCP Deep Research**: Comprehensive study of engulfing pattern implementations and box tracking systems
- ✅ **Technical Documentation**: Analyzed Pine Script v5 documentation for best practices

## Architecture Design

### Box Lifecycle States
- **ACTIVE**: Newly created box extending until touched
- **TOUCHED**: Price has intersected the box, no longer active
- **EXPIRED**: Box removed from tracking (optional cleanup)

### Data Structure
```pinescript
var array<box> boxes = array.new<box>()
var array<int> box_states = array.new<int>()
var array<int> box_creation_bars = array.new<int>()
var array<string> box_timeframes = array.new<string>()
var array<bool> box_is_bullish = array.new<bool>()
```

## Implementation Plan

### Phase 1: Core Pattern Detection ✅ IN PROGRESS
- [x] Basic engulfing candle detection logic
- [x] Volume and trend confirmation filters
- [x] Current timeframe pattern identification
- [ ] Pattern validation and testing

### Phase 2: Multi-Timeframe Integration
- [ ] Implement configurable timeframe inputs (15m, 1H, 4H, 1D)
- [ ] Efficient `request.security()` calls with tuple returns
- [ ] Non-repainting logic with proper lookahead settings
- [ ] Timeframe-specific border colors

### Phase 3: Box Lifecycle Management
- [ ] Box creation on engulfing detection
- [ ] Active box tracking arrays
- [ ] Box extension logic
- [ ] Price touch detection algorithm
- [ ] State transitions (ACTIVE → TOUCHED)

### Phase 4: Visual Features & UI
- [ ] Color-coded boxes by timeframe and pattern type
- [ ] Dynamic styling based on box status
- [ ] Optional labels showing timeframe and pattern info
- [ ] User customization options

### Phase 5: Optimization & Testing
- [ ] Performance optimization for multiple boxes
- [ ] Memory management and cleanup
- [ ] Alert conditions for patterns and touches
- [ ] Cross-market and timeframe testing

## Technical Requirements

### Engulfing Pattern Detection
```pinescript
// Bullish Engulfing Criteria:
// 1. Previous candle is bearish (close[1] < open[1])
// 2. Current candle is bullish (close > open)  
// 3. Current open < previous close
// 4. Current close > previous open
// 5. Optional: Volume confirmation
// 6. Optional: Trend alignment filter
```

### Box Management System
- **Creation**: `box.new()` with initial extension
- **Tracking**: Parallel arrays for metadata
- **Touch Detection**: `high >= box.get_bottom() and low <= box.get_top()`
- **State Updates**: Modify box appearance on status change
- **Cleanup**: Remove expired boxes to manage memory

### Multi-Timeframe Analysis
- Use `request.security()` with tuple returns for efficiency
- Non-repainting: `lookahead=barmerge.lookahead_on` with `[1]` offset
- Maximum 40 security calls limit management
- Timeframe validation against chart timeframe

## Key Features Implemented

### User Inputs
- [x] Timeframe selection (TF1-TF4) with enable/disable toggles
- [x] Pattern filters (volume, trend, minimum engulfing percentage)
- [x] Box styling options (colors, border width, extension)
- [x] Visual preferences (labels, colors by timeframe)

### Core Functions
- [x] `detect_engulfing()` - Pattern detection with filters
- [x] `get_tf_engulfing()` - Multi-timeframe data retrieval
- [x] `create_box()` - Box creation and labeling
- [x] `price_touches_box()` - Touch detection algorithm
- [x] `update_boxes()` - Box lifecycle management

### Performance Considerations
- Maximum 200 boxes (`max_boxes_count=200`)
- Efficient array operations with backward iteration
- Conditional security calls based on enabled timeframes
- Memory cleanup for touched boxes

## Testing Strategy

### Unit Testing
- [ ] Engulfing pattern detection accuracy
- [ ] Multi-timeframe data consistency  
- [ ] Box creation and positioning
- [ ] Touch detection precision

### Integration Testing
- [ ] Multiple active boxes management
- [ ] Cross-timeframe pattern correlation
- [ ] Performance under heavy box load
- [ ] Alert system functionality

### User Acceptance Testing
- [ ] Visual clarity and usability
- [ ] Customization options effectiveness
- [ ] Real-market performance validation

## Documentation Requirements

### Code Documentation
- Comprehensive inline comments
- Function parameter descriptions
- Algorithm explanations for complex logic

### User Guide
- Input parameter explanations
- Pattern recognition methodology
- Box lifecycle behavior description
- Performance optimization tips

## Research Resources Used

### Context7 MCP Documentation
- Pine Script v5 box drawing functions
- Multi-timeframe analysis with `request.security()`
- Candlestick pattern detection techniques
- Performance optimization guidelines

### EXA MCP Deep Research Findings
- Advanced engulfing pattern implementations
- Box lifecycle management best practices
- State management patterns for multiple objects
- Performance optimization for complex indicators
- Real-world Pine Script examples and patterns

## Success Criteria

### Functional Requirements
- ✅ Accurate engulfing pattern detection
- ✅ Multi-timeframe analysis capability
- ✅ Box creation and lifecycle management
- ✅ Price touch detection and state transitions
- ✅ Visual customization options

### Performance Requirements
- Handle up to 200 active boxes efficiently
- Maintain responsiveness with multiple timeframes
- Minimize `request.security()` calls for optimization
- Memory-efficient box cleanup and state management

### User Experience Requirements
- Intuitive input configuration
- Clear visual distinction between timeframes
- Informative labels and alerts
- Responsive real-time updates

## Future Enhancements
- Additional candlestick patterns (doji, hammer, etc.)
- Statistical analysis of pattern success rates
- Advanced filtering based on market conditions
- Integration with external data sources
- Mobile-optimized visualization options

---

## Important Notes for Future Development

**Always use Context7 MCP** when researching Pine Script documentation, TradingView API references, or technical analysis concepts. This ensures access to the most current and accurate information.

**Always use EXA MCP** for deep research when investigating complex implementation patterns, performance optimization techniques, or industry best practices. The deep research capability provides comprehensive insights from multiple sources.

This combination of tools provides the most effective research strategy for Pine Script development and technical analysis implementation.