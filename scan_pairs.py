import asyncio, os
from core import run_analysis
pairs = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X","AUDUSD=X","XAUUSD=X"]
tf = int(os.getenv("SCAN_TF","60"))
async def main():
    for s in pairs:
        print("\n"+run_analysis(s, tf, 240, None)+"\n")
asyncio.run(main())
