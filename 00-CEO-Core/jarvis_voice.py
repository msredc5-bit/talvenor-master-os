"""Jarvis — voice interface (STUB ONLY, Phase 0).

Jarvis = Main CEO Bot-এর ডাকনাম / voice মুখ। Boss কথা বলবেন Jarvis-কে,
Jarvis সেটা Main CEO Bot (brain)-এর কাছে পাঠাবে।

গুরুত্বপূর্ণ: Jarvis আর Main CEO Bot এক জিনিস নয় — আলাদা module।
Gemini-র folder map-এ ওরা একসাথে মিশে গিয়েছিল; এখানে আলাদা করা হয়েছে।

Status: STUB — এখনো live mic-এর সাথে যুক্ত নয়। Jarvis-এর আসল voice
কোড ~/workspace/jarvis-ceo-os-concept/ ও jarvis-os repo-তে আছে (আলাদা
project); Phase 1-এর পরে, Boss-এর সিদ্ধান্তে, এখানে জোড়া হবে।

এই ফাইলের কোনো function-ই এখন কাজ করে না — ডাকলে স্পষ্ট error দেয়,
চুপচাপ ভান করে না।
"""

STUB_NOTICE = "STUB — Jarvis voice interface not connected to a live mic yet (Phase 0)."


def listen():
    """Mic থেকে শোনা — এখনো বানানো হয়নি।"""
    raise NotImplementedError(STUB_NOTICE)


def speak(text):
    """Boss-কে voice-এ উত্তর দেওয়া — এখনো বানানো হয়নি।"""
    raise NotImplementedError(STUB_NOTICE)


def handle_voice_command(audio_input):
    """Voice command -> Main CEO Bot-এর কাছে পাঠানো — এখনো বানানো হয়নি।"""
    raise NotImplementedError(STUB_NOTICE)


if __name__ == "__main__":
    print(STUB_NOTICE)
    print("Real Jarvis concept docs: ~/workspace/jarvis-ceo-os-concept/")
    print("Real Jarvis code (separate repo): https://github.com/msredc5-bit/jarvis-os (PRIVATE)")
