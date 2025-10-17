Overview

The Advanced Password Strength & Breach Checker is a Python-based security tool designed to evaluate the strength of any password and check whether it has been exposed in known data breaches — all in a visually appealing, animated command-line interface.

The program uses entropy-based analysis and (optionally) the ZXCVBN password-strength library to determine how secure a password is. It also integrates with Have I Been Pwned (HIBP) API to detect whether a password has ever appeared in leaked datasets.

Animations, colorful feedback bars, and emoji-based strength meters make the experience interactive and educational for users.

🧠 How It Works (Summary)
Step-by-Step Process:

User Input:
You enter a password in the console.

Password Analysis:

The tool calculates entropy (randomness level).

If zxcvbn is installed, it uses it for a smarter, context-aware score.

A strength score (0–10) is derived based on character variety and length.

Feedback & Suggestions:

Displays a colorful 10-bar security level meter.

Provides tips like “add uppercase letters,” “use special symbols,” etc.

Breach Check (Have I Been Pwned API):

Your password’s SHA1 hash prefix is sent to HIBP’s range API (never your full password).

The response shows if your password exists in any public breach.

Safe and privacy-friendly!

Animations:

Spinner animation during processing.

Lock-safe animation if no breaches found 🔒

Lock-breach animation with cracking effect if the password was leaked 💥

Result Display:
Final feedback is shown, encouraging good password hygiene and manager use.

📦 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/<yourusername>/password-strength-breach-checker.git
cd password-strength-breach-checker

2️⃣ Install Requirements
pip install -r requirements.txt


Create a requirements.txt file with:

requests
colorama
zxcvbn

3️⃣ Run the Tool
python password_checker.py

🧩 Optional Dependencies

zxcvbn – for smarter strength estimation (optional)

pip install zxcvbn

🛡️ Privacy & Security Note

Passwords are never stored or sent in plain text.

The breach check uses only the first 5 characters of the SHA1 hash (HIBP’s k-Anonymity model).

Completely safe for personal or educational use.

🧑‍💻 Tech Stack

Language: Python 3

Libraries: requests, colorama, math, hashlib, zxcvbn

External API: Have I Been Pwned


Example Output
🔐  ADVANCED PASSWORD SECURITY CHECKER

👉 Enter your password: MyP@ssw0rd123
Analyzing password...

Security Level: [████████░░] 😊 Strong (8/10)
Entropy: 78.32 bits

💡 Feedback:
 - This is a strong password, but could be longer.

🧠 Suggestions:
   🔹 Consider increasing length to 16+ characters.
   🔸 Use a passphrase or password manager.

🔒  Password not found in breaches.
✅ Safe to use!
