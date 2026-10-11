"""Cuts the real night-walk screen recordings into one landscape video for YouTube (docs/media/night-walk.mp4).

Each scene is a stretch of a real recording (sped up where nothing happens), the phone on the left and a short
caption on the right. No audio: the iPhone recordings have street sound and voices in them.

    python3 docs/make_walk_video.py <redmi-without-contacts.mp4> <redmi-2.mp4> <iphone-language.mp4> <iphone-walk.mp4>
"""

import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

MEDIA = Path(__file__).parent / "media"
WORK = MEDIA / "raw" / "walk-video"
CHROMIUM = "/opt/pw-browsers/chromium"
W, H = 1920, 1080
PHONE_H = 960
PHONE_X, PHONE_Y = 260, 60

REDMI, REDMI_2, IPHONE_LANG, IPHONE = (Path(p) for p in sys.argv[1:5])

# (clip, start s, end s, speed, title, text, note). Starts and ends skip the Telegram contact list and the
# typed notes that are personal.
SCENES = [
    (REDMI, 5.5, 13.5, 1, "1 · The nudge",
     "A Telegram message at the hour I picked: “Hi Antonia 👋 Good time to head out. It's already dark · 16 °C, clear. "
     "Better a short walk on lit streets.”", "Tap “Salir a caminar” and the app opens."),
    (REDMI_2, 6, 56, 3, "2 · How are you arriving?",
     "“A bit tired but good.” The app already knows it's dark and 16 °C, so Gemma writes challenges for lit, busy "
     "streets, like “to unwind after your productive day, describe the brightest colour in the street lights.”",
     "Gemma (gemma4:31b, open weights) · ×3 speed"),
    (REDMI_2, 58, 90, 2.5, "3 · Answer with a photo",
     "Gemma's vision checks the photo against the challenge. A plant under a streetlamp: accepted.", "×2.5 speed"),
    (REDMI_2, 116, 150, 2.5, "4 · …and it's strict",
     "“A lit sign or shop window”, and I try some stone steps. Gemma: “some stone steps and a shadow, there's no lit "
     "sign or shop window.” Fair. 😅", "×2.5 speed"),
    (REDMI, 158, 205, 3, "5 · Or just say it",
     "A voice note, turned into text by ElevenLabs. You can still edit it before sending, and the audio is never stored.",
     "×3 speed"),
    (IPHONE, 25, 72, 2.5, "6 · Same walk, iPhone 16, English",
     "A note about dinner becomes “listen for a sound that reminds you of your dinner.” A streetlight photo: accepted.",
     "×2.5 speed"),
    (IPHONE, 75, 99, 3, "Answer of the night",
     "“I can hear some chickens moving around 😂🙈”", "×3 speed"),
    (IPHONE_LANG, 45, 53, 1, "7 · Change language mid-walk",
     "The challenges you already have keep their language; new ones come in English.", ""),
    (REDMI, 255, 285, 2, "8 · Close the walk",
     "10 minutes, 0.25 km and a few words: “I loved getting out at night and seeing there's life in the village, "
     "all lit up and calm.” No swaps: a perfect walk.", "×2 speed"),
    (REDMI_2, 232, 262, 2, "9 · It adds up",
     "A sticker unlocked, the notebook of 67 stickers and the week on the dashboard.", "×2 speed"),
]

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:%(W)dpx;height:%(H)dpx;background:#191e54;font-family:Inter,system-ui,sans-serif;color:#fff;overflow:hidden}
.phone{position:absolute;left:%(px)dpx;top:%(py)dpx;width:%(pw)dpx;height:%(ph)dpx;border-radius:44px;background:#0b0e2e;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.text{position:absolute;left:%(tx)dpx;right:140px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:28px}
h1{font-size:62px;line-height:1.05;margin:0;letter-spacing:-.02em;font-weight:800}
p{font-size:34px;line-height:1.4;margin:0;color:#dcdaf5;max-width:960px}
small{font-size:26px;color:#ffb300;font-weight:600}
.brand{position:absolute;right:140px;bottom:56px;font-size:24px;color:#a9a6d6;font-weight:600}
.real{position:absolute;right:140px;top:56px;font-size:22px;color:#10a878;font-weight:700;letter-spacing:.04em}
.center{left:0;right:0;text-align:center;align-items:center}
</style></head><body>%(body)s</body></html>"""


def phone_width():
    return round(PHONE_H * 1080 / 2400)


def card(page, path, body, phone=True):
    pw = phone_width()
    html = CARD % {"W": W, "H": H, "px": PHONE_X - 14, "py": PHONE_Y - 14, "pw": pw + 28, "ph": PHONE_H + 28,
                   "tx": PHONE_X + pw + 120, "body": ('<div class="phone"></div>' if phone else "") + body}
    page.set_content(html)
    page.screenshot(path=str(path))


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": W, "height": H})
        card(page, WORK / "title.png", """<div class="text center">
            <small>REAL SCREEN RECORDINGS · iPHONE 16 &amp; XIAOMI REDMI 12</small>
            <h1 style="font-size:96px">A night walk with Gemma</h1>
            <p style="font-size:40px;max-width:1300px">MicroAdventures: three tiny challenges, written by an open-weight model<br>for the time you have, the light that's left and how you feel.</p></div>""", phone=False)
        card(page, WORK / "end.png", """<div class="text center">
            <h1 style="font-size:80px">Go on, close the laptop 🌙</h1>
            <p style="font-size:42px">micro-adventure.onrender.com</p>
            <p style="font-size:32px">github.com/antoniahp/micro-adventure</p>
            <small>Gemma · Render · ElevenLabs · MongoDB Atlas · Sentry · Hacktoberfest 2026</small></div>""", phone=False)
        for i, (_, _, _, _, title, text, note) in enumerate(SCENES):
            card(page, WORK / f"scene-{i}.png", f"""<div class="real">● REAL WALK</div><div class="text"><h1>{title}</h1><p>{text}</p>
                {f'<small>{note}</small>' if note else ''}</div><div class="brand">MicroAdventures</div>""")
        browser.close()

    parts = []
    for still, seconds in (("title", 4), ("end", 5)):
        run("-loop", "1", "-t", str(seconds), "-i", str(WORK / f"{still}.png"), "-vf", "fps=30,format=yuv420p",
            "-c:v", "libx264", "-crf", "20", str(WORK / f"{still}.mp4"))
    parts.append(WORK / "title.mp4")
    pw = phone_width()
    for i, (clip, start, end, speed, *_ ) in enumerate(SCENES):
        out = WORK / f"scene-{i}.mp4"
        length = (end - start) / speed
        run("-ss", str(start), "-t", str(end - start), "-i", str(clip), "-loop", "1", "-t", f"{length:.3f}", "-i", str(WORK / f"scene-{i}.png"),
            "-filter_complex", f"[0:v]setpts=(PTS-STARTPTS)/{speed},scale={pw}:{PHONE_H}:force_original_aspect_ratio=decrease,"
                               f"pad={pw}:{PHONE_H}:(ow-iw)/2:(oh-ih)/2:color=#0b0e2e,fps=30[v];"
                               f"[1:v][v]overlay={PHONE_X}:{PHONE_Y}:shortest=1,format=yuv420p",
            "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-t", f"{length:.3f}", str(out))
        parts.append(out)
    parts.append(WORK / "end.mp4")
    (WORK / "list.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run("-f", "concat", "-safe", "0", "-i", str(WORK / "list.txt"), "-c:v", "libx264", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(MEDIA / "night-walk.mp4"))
    print(MEDIA / "night-walk.mp4")


if __name__ == "__main__":
    main()
