import time
import sys
import hashlib
import requests
import os
import math
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

try:
    from zxcvbn import zxcvbn
    HAS_ZXCVBN = True
except ImportError:
    HAS_ZXCVBN = False


# === Animation helpers ===
def spinner_animation(duration=2, message="Processing"):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    for i in range(int(duration / 0.1)):
        sys.stdout.write(f"\r{Fore.CYAN}{message} {frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")


def smooth_text(text, delay=0.02):
    """Print text with typing animation."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# === Lock animations ===
def lock_safe_animation(duration=1.8):
    """Simple safe/locked animation (plays when password NOT found breached)."""
    frames = [
        "🔒",
        "🔒",
        "🔒",
        "🔐",
        "🔐",
        "🔒"
    ]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write("\r" + Fore.GREEN + frames[i % len(frames)] + "  Password not found in breaches.")
        sys.stdout.flush()
        time.sleep(0.18)
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")


def lock_breach_animation(count, duration=3.0):
    """Lock breaking animation (plays when password found in breaches)."""
    # frames portray lock cracking and breaking; use emojis + ascii
    frames = [
        "🔒",
        "🔓",
        "🔐",
        "🔒",
        "🔓",
        "🔓💥",
        "🔓💥",
        "🧨💥",
        "💥",
        "⛔ CRACKED ⛔"
    ]
    # Start with a dramatic countdown
    for sec in range(3, 0, -1):
        sys.stdout.write(f"\r{Fore.RED}!! Breach detected !! Preparing animation in {sec}...")
        sys.stdout.flush()
        time.sleep(0.6)
    # run frames
    start = time.time()
    i = 0
    while time.time() - start < duration:
        frame = frames[i % len(frames)]
        if "CRACKED" in frame or "💥" in frame:
            color = Fore.RED + Style.BRIGHT
        else:
            color = Fore.YELLOW
        sys.stdout.write("\r" + color + frame + f"   This password appeared in {count} breach(es)!")
        sys.stdout.flush()
        time.sleep(0.25 + (i % 3) * 0.05)
        i += 1
    # final dramatic message
    sys.stdout.write("\r" + Fore.RED + Style.BRIGHT + f"❌ PASSWORD BREACHED — seen {count} times. Change it now!     \n")
    sys.stdout.flush()


# === Password Analysis ===
def rule_based_score(pw):
    length = len(pw)
    lower = any(c.islower() for c in pw)
    upper = any(c.isupper() for c in pw)
    digits = any(c.isdigit() for c in pw)
    symbols = any(not c.isalnum() for c in pw)
    pool = 0
    if lower:
        pool += 26
    if upper:
        pool += 26
    if digits:
        pool += 10
    if symbols:
        pool += 32
    entropy = length * math.log2(pool) if pool > 0 else 0
    # scale entropy to 0-10, cap
    score = max(0, min(10, int(entropy / 10)))
    return score, entropy


def analyze_password(pw):
    if not pw:
        return {"score": 0, "entropy": 0, "feedback": ["Empty password."]}
    if HAS_ZXCVBN:
        res = zxcvbn(pw)
        # zxcvbn score: 0..4 -> scale to 0..10
        score = int((res.get("score", 0) / 4) * 10)
        entropy = res.get("entropy", 0)
        feedback = []
        if res.get("feedback", {}).get("warning"):
            feedback.append(res["feedback"]["warning"])
        feedback += res.get("feedback", {}).get("suggestions", [])
        return {"score": score, "entropy": entropy, "feedback": feedback}
    else:
        score, entropy = rule_based_score(pw)
        return {"score": score, "entropy": entropy, "feedback": ["Rule-based scoring used."]}


# === Strength bar (10 levels) ===
def strength_bar(score):
    total_bars = 10
    filled = int(score)
    if score <= 3:
        color = Fore.RED
        mood = "😨 Weak"
    elif score <= 6:
        color = Fore.YELLOW
        mood = "😐 Medium"
    elif score <= 8:
        color = Fore.LIGHTGREEN_EX
        mood = "😊 Strong"
    else:
        color = Fore.GREEN
        mood = "💪 Very Strong"
    bar = color + "█" * filled + Fore.WHITE + "░" * (total_bars - filled)
    print(f"\nSecurity Level: [{bar}] {mood} ({score}/10)\n")


# === Suggestions based on weaknesses ===
def improvement_tips(pw):
    tips = []
    if len(pw) < 12:
        tips.append("🔹 Increase password length to at least 12–16 characters.")
    if not any(c.isupper() for c in pw):
        tips.append("🔹 Add uppercase letters (A–Z).")
    if not any(c.islower() for c in pw):
        tips.append("🔹 Add lowercase letters (a–z).")
    if not any(c.isdigit() for c in pw):
        tips.append("🔹 Include numbers (0–9).")
    if not any(not c.isalnum() for c in pw):
        tips.append("🔹 Add special characters (!, @, #, $, %, &, *).")
    if pw.lower() in ["password", "admin", "123456", "qwerty"]:
        tips.append("🔹 Avoid common passwords — be unique!")
    if len(tips) == 0:
        tips.append("✅ Great job! Your password is well balanced.")
    # Extra suggestions for advanced users
    tips.append("🔸 Consider using a passphrase (multiple random words) or a password manager.")
    return tips


# === Check for breaches using Have I Been Pwned API ===
def hibp_password_pwned(password):
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        spinner_animation(1.8, "Checking breach databases")
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return -1
        for line in r.text.splitlines():
            suf, count = line.split(":")
            if suf == suffix:
                return int(count)
        return 0
    except Exception:
        return -1


# === Main ===
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + "🔐  ADVANCED PASSWORD SECURITY CHECKER\n")
    smooth_text("Welcome! This tool analyzes your password, suggests improvements, and checks known breaches.\n")

    try:
        pw = input(Fore.YELLOW + "👉 Enter your password: " + Style.RESET_ALL)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return

    spinner_animation(1.2, "Analyzing password")

    result = analyze_password(pw)
    score = result["score"]
    entropy = result["entropy"]
    feedback = result["feedback"]

    strength_bar(score)
    print(Fore.CYAN + f"Entropy: {Fore.WHITE}{entropy:.2f} bits\n")

    if feedback:
        print(Fore.MAGENTA + "💡 Analysis Feedback:")
        for f in feedback:
            print(Fore.LIGHTBLACK_EX + "   - " + f)
        print()

    print(Fore.CYAN + "🧠 Improvement Suggestions:")
    for tip in improvement_tips(pw):
        print(Fore.WHITE + "   " + tip)
    print()

    # Check breach and animate lock accordingly
    count = hibp_password_pwned(pw)
    if count == -1:
        print(Fore.RED + "\n⚠ Could not connect to HIBP API.")
    elif count == 0:
        # Safe animation
        lock_safe_animation(1.8)
        print(Fore.GREEN + "\n✅ Your password was NOT found in known breaches.")
    else:
        # Breach animation
        lock_breach_animation(count, duration=3.2)

    print(Fore.CYAN + "\nStay safe — consider using a password manager and unique passwords for each site! 🚀\n")


# === Entry point ===
if __name__ == "__main__":
    main()
