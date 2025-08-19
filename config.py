from datetime import timedelta

SPREAD_PIPS = {
    "EURUSD=X": 1.2,
    "GBPUSD=X": 1.5,
    "USDJPY=X": 1.3,
    "XAUUSD=X": 25.0,
    "XAGUSD=X": 30.0,
}
WEIGHTS_16 = {
    "ema_cross_9_21":1,"ema_cross_20_50":1,"rsi_zone":1,"rsi_div":1,"macd_hist_flip":1,"macd_cross":1,
    "adx_trend":1,"atr_zone":1,"candle_pattern":1,"mtf_confluence":1,"fibo_touch":1,"sr_break":1,
    "high_volume":1,"momentum_body":1,"no_opposing_htf":1,"price_above_200":1
}
WEIGHTS_6 = {
    "no_red_news_1h":1,"news_sentiment_ok":1,"no_cb_conflict":1,"spread_ok":1,"tg_agreement":1,"not_mid_candle":1
}
EMA_FAST_1, EMA_SLOW_1 = 9, 21
EMA_FAST_2, EMA_SLOW_2 = 20, 50
EMA_LONG = 200
RSI_LEN = 14
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9
ADX_LEN = 14
ATR_LEN = 14
VOL_MA = 20
MFI_LEN = 14
OBV_MA = 20
TF_MAP = {"H1":60, "H4":240, "D1":1440}
LOOKBACK = 400
MID_CANDLE_GUARD_FRAC = 0.15
ATR_SL = 1.5
ATR_TP = 2.5
