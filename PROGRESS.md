Last updated: 2025-08-19 07:59Z
# Project Progress Tracker

---

## 🟡 Golden Rules
- Always deliver **full files**, never trimmed or partial.  
- Default is **EOF paste** (`cat > file <<'EOF' ... EOF`) for updates.  
- Use `rm -f file && nano file` **only if explicitly requested**.  
- Every update must stay consistent with other files (no breaking imports).  
- Keep **error log** alive for tracking issues; don’t overwrite history blindly.  

---

## ✅ Last Completed
- Switched data source to **TwelveData**; API key loaded via `.env`.  
- Disabled Yahoo fallback (`YF_DISABLE=1`) to avoid bad JSON.  
- Added `logutil.py` + `run.py` and **errors.log** (INFO/ERROR) with `LOG_FILE` & `LOG_LEVEL`.  
- Rebuilt **core.py** and **main.py** (clean imports, ATR/RSI, simple risk plan).  
- Smoke tests: `get_candles()` OK for USD/JPY, EUR/USD, XAU/USD (TD H1); `main.py` prints signals.  

---

## ⚠️ Current Status
- Analysis & signal printout working.  
- Telegram sending is **off** (by flag).  
- Multi-symbol runner exists as manual loop (not scheduled).  
- Error log working; no rotation yet.  

---

## ⏭️ Next Steps
1. **Telegram alerts**: enable `tg_send()` path and test `/start.sh` with `--no-telegram` off.  
2. **Multi-symbol loop**: add a driver to iterate `[USD/JPY, EUR/USD, XAU/USD]` and write one combined message.  
3. **Scheduler**: simple `termux-job-scheduler` / while-loop / cron-style runner for H1/H4 cadence.  
4. **Paper trading**: append “paper ledger” CSV (timestamp, symbol, side, px, size, ATR stop).  
5. **Config**: move symbols/TF/position sizing to `.env` (ENV-first).  
6. **Logs**: add rotation (keep last N files) and a `--debug` switch for verbose.  

---

## 📜 Milestones
- [✔] TwelveData verified by curl and Python (`get_candles` OK).  
- [✔] Yahoo path disabled; JSONDecode errors no longer block.  
- [✔] Core/Main synchronized; import issues resolved.  
- [✔] Centralized error logging with `run.py` wrapper.  
- [ ] Telegram alerts live.  
- [ ] Scheduler & paper trading.  
- [ ] Final “ship mode”.  

---

## 🛠 Handy Commands
- View progress: `cat PROGRESS.md`  
- Live log: `tail -f errors.log`  
- One-off run: `python main.py --symbol "USD/JPY" --tf 60 --no-telegram`  
- Wrapped run with logging: `./start.sh "USD/JPY" 60`  

