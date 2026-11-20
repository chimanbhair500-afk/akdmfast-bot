import os
import math
import time
import random
from datetime import datetime, timezone, timedelta
import requests

# ==========================================
# 1. मुख्य सेटिंग्स (Railway/Render Variables या सीधे यहाँ)
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9180015929:AAHJ7DsY43S19oeo89xLpOVu_7Abs6oX2Xw")  #[span_1](start_span)[span_1](end_span)
CHANNEL_ID = "@akdmfast_official"  #[span_2](start_span)[span_2](end_span)
CHANNEL_DISPLAY_NAME = "AK Dmfast official"  #[span_3](start_span)[span_3](end_span)[span_4](start_span)[span_4](end_span)
GAME_LINK = "https://dry-band-8d5a.rathvamiitu.workers.dev"
FIREBASE_DB_URL = "https://ak-dmfast-default-rtdb.firebaseio.com"

# तीनों पोस्टर के डायरेक्ट लिंक
POSTER_SESSION_START = "https://i.ibb.co/7NrrKMz2/Screenshot-20261119-223043.jpg"  #[span_5](start_span)[span_5](end_span)
POSTER_SESSION_CLOSE = "https://i.ibb.co/F9HB3jb/Screenshot-20261119-223046.jpg"  #[span_6](start_span)[span_6](end_span)
POSTER_SURE_SHOT = "https://i.ibb.co/9kHkQ8sc/Screenshot-20261119-223011.jpg"  #[span_7](start_span)[span_7](end_span)

# भारतीय समय (IST = UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# आपके 6 सेशन के समय (घंटा, मिनट)
SESSIONS = [
    (8, 30),
    (11, 0),
    (13, 0),   # दोपहर 1:00 बजे
    (16, 30),  # शाम 4:30 बजे
    (19, 30),  # शाम 7:30 बजे
    (21, 30),  # रात 9:30 बजे
]

# डुप्लीकेट मैसेज रोकने के लिए ट्रैकर
sent_events = set()

# ==========================================
# 2. Telegram API हेल्पर फ़ंक्शन
# ==========================================
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=15).json()
        if not res.get("ok"):
            print(f"[Telegram Error - Message]: {res.get('description')}")
        return res.get("ok", False)
    except Exception as e:
        print(f"[Network Error - Message]: {e}")
        return False

def send_telegram_photo(photo_url, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption
    }
    try:
        res = requests.post(url, data=payload, timeout=20).json()
        if not res.get("ok"):
            print(f"[Telegram Error - Photo]: {res.get('description')}")
        return res.get("ok", False)
    except Exception as e:
        print(f"[Network Error - Photo]: {e}")
        return False

# ==========================================
# 3. गेम से WinGo 1-Minute पीरियड और रिज़ल्ट निकालना
# ==========================================
def get_wingo_1m_info():
    """आपकी गेम के exact UTC फॉर्मूले से वर्तमान 1-मिनट पीरियड निकालता है"""
    now_utc = datetime.now(timezone.utc)
    yyyy = now_utc.strftime("%Y")
    mm = now_utc.strftime("%m")
    dd = now_utc.strftime("%d")
    total_seconds = (now_utc.hour * 3600) + (now_utc.minute * 60) + now_utc.second

    sec = 60
    round_index = (total_seconds // sec) + 1
    remaining = sec - (total_seconds % sec)
    full_period = int(f"{yyyy}{mm}{dd}{sec}{str(round_index).zfill(4)}")
    short_period = str(full_period)[-3:]  # आखिरी 3 अंक (जैसे 070, 071)

    return full_period, short_period, remaining

def get_game_actual_outcome(full_period):
    """आपकी गेम के exact लॉजिक और Firebase forcedResults/60 से Big/Small निकालता है"""
    forced_val = None
    try:
        fb_res = requests.get(f"{FIREBASE_DB_URL}/forcedResults/60.json", timeout=5)
        if fb_res.status_code == 200 and fb_res.json() is not None:
            forced_val = str(fb_res.json())
    except Exception:
        pass

    winning_num = int(math.floor(abs(math.sin(full_period) * 10000))) % 10

    if forced_val is not None:
        if forced_val == "Green":
            winning_num = 7
        elif forced_val == "Red":
            winning_num = 2
        elif forced_val == "Violet":
            winning_num = 0
        elif forced_val == "Big":
            winning_num = 8
        elif forced_val == "Small":
            winning_num = 3
        elif forced_val.isdigit():
            winning_num = int(forced_val)

    return "Big" if winning_num >= 5 else "Small"

# ==========================================
# 4. 7 Win और 8 Loss का बदलता (अप्रत्याशित) पैटर्न जनरेटर
# ==========================================
def generate_unpredictable_session_plan():
    """कुल 15 राउंड (7 Win + 8 Loss) को हर सेशन में अलग-अलग रैंडम क्रम में बनाता है"""
    outcomes = ["WIN"] * 7 + ["LOSS"] * 8
    random.shuffle(outcomes)
    # लगातार 4 से ज़्यादा एक जैसे परिणाम न आएं, इसके लिए हल्का संतुलन
    for _ in range(10):
        has_streak = False
        for i in range(len(outcomes) - 3):
            if outcomes[i] == outcomes[i+1] == outcomes[i+2] == outcomes[i+3]:
                has_streak = True
                break
        if not has_streak:
            break
        random.shuffle(outcomes)
    return outcomes

# ==========================================
# 5. विशेष फॉर्मेट वाले संदेश
# ==========================================
def send_game_link_post():
    msg = (
        f"{CHANNEL_DISPLAY_NAME}\n"
        f"REGISTRATION LINK ✔️\n\n"
        f"{GAME_LINK}"
    )  #[span_8](start_span)[span_8](end_span)
    send_telegram_message(msg)

def send_prediction_post(short_period, predicted_side, multiplier_step):
    msg = (
        f"🔴 WIN GO 1 MINUTE 🟢\n"
        f"★★★★★★\n"
        f"{short_period} > {predicted_side} > {multiplier_step}x"
    )  #[span_9](start_span)[span_9](end_span)
    send_telegram_message(msg)

# ==========================================
# 6. मुख्य ऑटोमेशन लूप
# ==========================================
def run_bot():
    print("🚀 AK Dmfast Official Prediction Bot Started...")
    active_session = None

    while True:
        now_ist = datetime.now(IST)
        today_str = now_ist.strftime("%Y-%m-%d")

        # हर सेशन के प्री-लिंक (10 मिनट पहले), स्टार्ट पोस्टर (1 मिनट पहले) और सेशन शुरू होने की जाँच
        for idx, (s_hour, s_min) in enumerate(SESSIONS):
            session_start_dt = now_ist.replace(hour=s_hour, minute=s_min, second=0, microsecond=0)
            pre_link_dt = session_start_dt - timedelta(minutes=10)
            start_poster_dt = session_start_dt - timedelta(minutes=1)

            # 1) सेशन शुरू होने से 10 मिनट पहले गेम की लिंक भेजना
            pre_key = f"{today_str}_S{idx}_PRELINK"
            if pre_link_dt <= now_ist < pre_link_dt + timedelta(seconds=20) and pre_key not in sent_events:
                sent_events.add(pre_key)
                print(f"[{now_ist.strftime('%H:%M:%S')}] Sending 10-min pre-session game link...")
                send_game_link_post()

            # 2) सेशन शुरू होने से 1 मिनट पहले Session Start पोस्टर भेजना
            poster_key = f"{today_str}_S{idx}_STARTPOSTER"
            if start_poster_dt <= now_ist < start_poster_dt + timedelta(seconds=20) and poster_key not in sent_events:
                sent_events.add(poster_key)
                print(f"[{now_ist.strftime('%H:%M:%S')}] Sending Session Start poster...")
                send_telegram_photo(POSTER_SESSION_START)

            # 3) ठीक सेशन के समय (8:30, 11:00, 13:00, 16:30, 19:30, 21:30) पर 15 राउंड का सेशन चालू करना
            sess_key = f"{today_str}_S{idx}_ACTIVE"
            if session_start_dt <= now_ist < session_start_dt + timedelta(seconds=20) and sess_key not in sent_events:
                sent_events.add(sess_key)
                plan = generate_unpredictable_session_plan()
                active_session = {
                    "id": sess_key,
                    "plan": plan,          # 7 WIN और 8 LOSS का रैंडम क्रम
                    "step": 0,             # 0 से 14 तक (कुल 15 राउंड)
                    "loss_streak": 0,      # मल्टीप्लायर (1x, 3x, 8x...) के लिए
                    "current_round": None  # वर्तमान में चल रहा राउंड डेटा
                }
                print(f"[{now_ist.strftime('%H:%M:%S')}] Session {idx+1} Started! Plan: {plan}")

        # 4) सक्रिय सेशन के अंदर हर 1-मिनट राउंड का प्रेडिक्शन और रिज़ल्ट संभालना
        if active_session is not None:
            full_period, short_period, remaining = get_wingo_1m_info()
            cur = active_session["current_round"]

            # अगर कोई राउंड चल रहा है और उसका पीरियड बदल गया है (यानी राउंड खत्म हो गया)
            if cur is not None and cur["full_period"] != full_period:
                if cur["target_outcome"] == "WIN":
                    print(f"[{now_ist.strftime('%H:%M:%S')}] Round {cur['short_period']} WON! Sending Sure Shot poster...")
                    send_telegram_photo(POSTER_SURE_SHOT)
                    active_session["loss_streak"] = 0
                else:
                    print(f"[{now_ist.strftime('%H:%M:%S')}] Round {cur['short_period']} LOSS.")
                    active_session["loss_streak"] += 1

                active_session["current_round"] = None
                active_session["step"] += 1

                # अगर सभी 15 राउंड (7 Win + 8 Loss) पूरे हो गए तो सेशन क्लोज़ करें
                if active_session["step"] >= len(active_session["plan"]):
                    print(f"[{now_ist.strftime('%H:%M:%S')}] Session Finished! Sending Session Close poster & Game Link...")
                    time.sleep(2)
                    send_telegram_photo(POSTER_SESSION_CLOSE)
                    time.sleep(2)
                    send_game_link_post()
                    active_session = None

            # नया राउंड शुरू होने पर (जब राउंड में 45 से 58 सेकंड बाकी हों) नया प्रेडिक्शन भेजना
            if active_session is not None and active_session["current_round"] is None:
                if 45 <= remaining <= 58:
                    step_idx = active_session["step"]
                    target_outcome = active_session["plan"][step_idx]
                    actual_side = get_game_actual_outcome(full_period)

                    # गेम के असली रिज़ल्ट के आधार पर प्रेडिक्शन तय करना
                    if target_outcome == "WIN":
                        predicted_side = actual_side
                    else:
                        predicted_side = "Small" if actual_side == "Big" else "Big"

                    # हार के बाद 1x -> 3x -> 8x -> 24x स्टेप
                    mult_table = [1, 3, 8, 24, 72]
                    mult_val = mult_table[min(active_session["loss_streak"], len(mult_table) - 1)]

                    send_prediction_post(short_period, predicted_side, mult_val)
                    active_session["current_round"] = {
                        "full_period": full_period,
                        "short_period": short_period,
                        "target_outcome": target_outcome,
                        "predicted_side": predicted_side
                    }
                    print(f"[{now_ist.strftime('%H:%M:%S')}] Sent Prediction: {short_period} > {predicted_side} > {mult_val}x ({target_outcome})")

        # पुरानी तारीख के ट्रैकर साफ़ रखना
        if len(sent_events) > 200:
            sent_events.clear()

        time.sleep(1)

if __name__ == "__main__":
    run_bot()
