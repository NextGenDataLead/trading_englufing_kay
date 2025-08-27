//@version=5
indicator("MTF Engulfing Horizontal Boxes", shorttitle="MTF Engulfing Zones", overlay=true, max_boxes_count=500)

// Input parameters
timeframe1 = input.timeframe("5", "Timeframe 1", group="Timeframes")
timeframe2 = input.timeframe("15", "Timeframe 2", group="Timeframes")
timeframe3 = input.timeframe("60", "Timeframe 3", group="Timeframes")
show_tf1 = input.bool(true, "Show Timeframe 1", group="Display")
show_tf2 = input.bool(true, "Show Timeframe 2", group="Display")
show_tf3 = input.bool(true, "Show Timeframe 3", group="Display")

// Box appearance settings
tf1_bull_color = input.color(color.new(color.green, 90), "TF1 Bullish", group="TF1 Colors", inline="tf1")
tf1_bear_color = input.color(color.new(color.red, 90), "TF1 Bearish", group="TF1 Colors", inline="tf1")
tf2_bull_color = input.color(color.new(color.blue, 85), "TF2 Bullish", group="TF2 Colors", inline="tf2")
tf2_bear_color = input.color(color.new(color.orange, 85), "TF2 Bearish", group="TF2 Colors", inline="tf2")
tf3_bull_color = input.color(color.new(color.purple, 80), "TF3 Bullish", group="TF3 Colors", inline="tf3")
tf3_bear_color = input.color(color.new(color.yellow, 80), "TF3 Bearish", group="TF3 Colors", inline="tf3")

// Active box settings
box_transparency = input.int(70, "Box Transparency", minval=0, maxval=95, group="Box Settings")
box_border_width = input.int(2, "Border Width", minval=1, maxval=4, group="Box Settings")
extend_right_bars = input.int(500, "Extend Right (Bars)", minval=50, maxval=2000, group="Box Settings")

// Enhanced engulfing detection
detect_engulfing() =>
    // Previous and current candle data
    o1 = open[1]
    c1 = close[1]
    h1 = high[1]
    l1 = low[1]
    
    o0 = open
    c0 = close
    h0 = high
    l0 = low
    
    // Body sizes
    prev_body = math.abs(c1 - o1)
    curr_body = math.abs(c0 - o0)
    
    // Minimum body size (using ATR for dynamic sizing)
    min_body = ta.atr(20) * 0.2
    
    // Bullish engulfing pattern
    prev_red = c1 < o1
    curr_green = c0 > o0
    bullish_engulf = prev_red and curr_green and o0 <= c1 and c0 >= o1 and curr_body > prev_body and prev_body >= min_body
    
    // Bearish engulfing pattern  
    prev_green = c1 > o1
    curr_red = c0 < o0
    bearish_engulf = prev_green and curr_red and o0 >= c1 and c0 <= o1 and curr_body > prev_body and prev_body >= min_body
    
    // Box coordinates for horizontal rectangles
    bull_top = bullish_engulf ? math.max(h0, h1, o0, c0) : na
    bull_bottom = bullish_engulf ? math.min(l0, l1, o0, c0) : na
    bear_top = bearish_engulf ? math.max(h0, h1, o0, c0) : na  
    bear_bottom = bearish_engulf ? math.min(l0, l1, o0, c0) : na
    
    [bullish_engulf, bearish_engulf, bull_top, bull_bottom, bear_top, bear_bottom]

// Get signals from different timeframes
[tf1_bull_signal, tf1_bear_signal, tf1_bull_top, tf1_bull_bottom, tf1_bear_top, tf1_bear_bottom] = 
     request.security(syminfo.tickerid, timeframe1, detect_engulfing())

[tf2_bull_signal, tf2_bear_signal, tf2_bull_top, tf2_bull_bottom, tf2_bear_top, tf2_bear_bottom] = 
     request.security(syminfo.tickerid, timeframe2, detect_engulfing())

[tf3_bull_signal, tf3_bear_signal, tf3_bull_top, tf3_bull_bottom, tf3_bear_top, tf3_bear_bottom] = 
     request.security(syminfo.tickerid, timeframe3, detect_engulfing())

// Box management structure
type EngulfingBox
    box rect
    float top_level
    float bottom_level  
    bool is_bullish
    string timeframe
    int creation_bar
    color original_color
    bool is_closed
    bool price_has_exited

var array<EngulfingBox> all_boxes = array.new<EngulfingBox>()

// Function to create horizontal rectangular boxes
create_horizontal_box(is_bull, top_price, bottom_price, tf_name, bull_color, bear_color) =>
    if not na(top_price) and not na(bottom_price) and barstate.isconfirmed
        
        // Choose colors
        base_color = is_bull ? bull_color : bear_color
        box_color = color.new(base_color, box_transparency)
        border_color = color.new(base_color, 50)
        
        // Create horizontal rectangle extending far to the right
        new_box = box.new(
             left = bar_index - 1,
             top = top_price,
             right = bar_index + extend_right_bars, 
             bottom = bottom_price,
             bgcolor = box_color,
             border_color = border_color,
             border_width = box_border_width,
             extend = extend.right)
        
        // Add text label on the box
        label_text = tf_name + (is_bull ? " BULL ZONE" : " BEAR ZONE")
        label.new(
             x = bar_index + 5,
             y = (top_price + bottom_price) / 2,
             text = label_text,
             style = label.style_label_left,
             color = color.new(base_color, 30),
             textcolor = color.white,
             size = size.small)
        
        // Store the box data
        new_engulfing_box = EngulfingBox.new(
             rect = new_box,
             top_level = top_price,
             bottom_level = bottom_price,
             is_bullish = is_bull,
             timeframe = tf_name,
             creation_bar = bar_index,
             original_color = base_color,
             is_closed = false,
             price_has_exited = false)
        
        array.push(all_boxes, new_engulfing_box)

// Create boxes for each timeframe
if show_tf1
    if tf1_bull_signal
        create_horizontal_box(true, tf1_bull_top, tf1_bull_bottom, timeframe1, tf1_bull_color, tf1_bear_color)
    if tf1_bear_signal
        create_horizontal_box(false, tf1_bear_top, tf1_bear_bottom, timeframe1, tf1_bull_color, tf1_bear_color)

if show_tf2  
    if tf2_bull_signal
        create_horizontal_box(true, tf2_bull_top, tf2_bull_bottom, timeframe2, tf2_bull_color, tf2_bear_color)
    if tf2_bear_signal
        create_horizontal_box(false, tf2_bear_top, tf2_bear_bottom, timeframe2, tf2_bull_color, tf2_bear_color)

if show_tf3
    if tf3_bull_signal  
        create_horizontal_box(true, tf3_bull_top, tf3_bull_bottom, timeframe3, tf3_bull_color, tf3_bear_color)
    if tf3_bear_signal
        create_horizontal_box(false, tf3_bear_top, tf3_bear_bottom, timeframe3, tf3_bull_color, tf3_bear_color)

// Variables to track retests for plotting
var bool bull_retest = false
var bool bear_retest = false
var color retest_color_bull = color.green
var color retest_color_bear = color.red

// Check for price retracement to boxes and CLOSE them at retest point
if array.size(all_boxes) > 0 and barstate.isconfirmed
    bull_retest := false
    bear_retest := false
    
    for i = 0 to array.size(all_boxes) - 1
        engulfing_box = array.get(all_boxes, i)
        
        // Only process boxes that are still open (not closed yet)
        if not engulfing_box.is_closed
            // Check if current candle touches the box zone
            candle_in_box = not (low > engulfing_box.top_level or high < engulfing_box.bottom_level)
            
            // Additional check: make sure we're not on the creation bar
            bars_since_creation = bar_index - engulfing_box.creation_bar
            
            if bars_since_creation > 1
                // If price is NOT in the box, mark that price has exited
                if not candle_in_box
                    engulfing_box.price_has_exited := true
                
                // If price IS in the box AND price has previously exited, close the box
                if candle_in_box and engulfing_box.price_has_exited
                    
                    // Set retest flags for plotting
                    if engulfing_box.is_bullish
                        bull_retest := true
                        retest_color_bull := engulfing_box.original_color
                    else
                        bear_retest := true
                        retest_color_bear := engulfing_box.original_color
                    
                    // CLOSE the box at current bar (stop extending right)
                    box.set_right(engulfing_box.rect, bar_index)
                    
                    // Mark as closed
                    engulfing_box.is_closed := true
                    
                    // Change appearance to show it's been retested
                    retested_color = color.new(engulfing_box.original_color, box_transparency + 15)
                    border_color = color.new(engulfing_box.original_color, 20)
                    box.set_bgcolor(engulfing_box.rect, retested_color)
                    box.set_border_color(engulfing_box.rect, border_color)

// Plot retest signals
plotshape(bull_retest, "Bull Zone Retest", shape.circle, location.belowbar, 
          retest_color_bull, size=size.small)
plotshape(bear_retest, "Bear Zone Retest", shape.square, location.abovebar, 
          retest_color_bear, size=size.small)

// Update box right edges to keep them current (only for boxes that aren't closed)
if barstate.islast and array.size(all_boxes) > 0
    for i = 0 to array.size(all_boxes) - 1
        engulfing_box = array.get(all_boxes, i)
        // Only extend boxes that haven't been closed by retest
        if not engulfing_box.is_closed
            box.set_right(engulfing_box.rect, bar_index + extend_right_bars)

// Plot entry signals with different shapes for each timeframe
plotshape(show_tf1 and tf1_bull_signal, "TF1 Bull Entry", shape.triangleup, 
          location.belowbar, tf1_bull_color, size=size.tiny)
plotshape(show_tf1 and tf1_bear_signal, "TF1 Bear Entry", shape.triangledown, 
          location.abovebar, tf1_bear_color, size=size.tiny)

plotshape(show_tf2 and tf2_bull_signal, "TF2 Bull Entry", shape.arrowup, 
          location.belowbar, tf2_bull_color, size=size.small)
plotshape(show_tf2 and tf2_bear_signal, "TF2 Bear Entry", shape.arrowdown, 
          location.abovebar, tf2_bear_color, size=size.small)

plotshape(show_tf3 and tf3_bull_signal, "TF3 Bull Entry", shape.flag, 
          location.belowbar, tf3_bull_color, size=size.normal)
plotshape(show_tf3 and tf3_bear_signal, "TF3 Bear Entry", shape.flag, 
          location.abovebar, tf3_bear_color, size=size.normal)

// Information table
if barstate.islast
    var table info_table = table.new(position.top_right, 2, 6, 
                                   bgcolor=color.white, border_width=1, border_color=color.gray)
    
    // Header
    table.cell(info_table, 0, 0, "Engulfing Zones", text_color=color.white, bgcolor=color.navy)
    table.cell(info_table, 1, 0, "Count", text_color=color.white, bgcolor=color.navy)
    
    // Count boxes by status
    total_boxes = array.size(all_boxes)
    open_boxes = 0
    closed_boxes = 0
    
    if total_boxes > 0
        for i = 0 to total_boxes - 1
            box_data = array.get(all_boxes, i)
            if box_data.is_closed
                closed_boxes += 1
            else
                open_boxes += 1
    
    table.cell(info_table, 0, 1, "Total Boxes", text_color=color.black)
    table.cell(info_table, 1, 1, str.tostring(total_boxes), text_color=color.black)
    
    table.cell(info_table, 0, 2, "Open", text_color=color.green)
    table.cell(info_table, 1, 2, str.tostring(open_boxes), text_color=color.green)
    
    table.cell(info_table, 0, 3, "Closed", text_color=color.orange)
    table.cell(info_table, 1, 3, str.tostring(closed_boxes), text_color=color.orange)
    
    // Active timeframes
    active_tfs = ""
    if show_tf1
        active_tfs := active_tfs + timeframe1 + " "
    if show_tf2  
        active_tfs := active_tfs + timeframe2 + " "
    if show_tf3
        active_tfs := active_tfs + timeframe3
        
    table.cell(info_table, 0, 4, "Timeframes", text_color=color.black)
    table.cell(info_table, 1, 4, active_tfs, text_color=color.black)
    
    table.cell(info_table, 0, 5, "Status", text_color=color.black)  
    table.cell(info_table, 1, 5, "Running", text_color=color.green)
