"""Joins the clips recorded by record_demo.py into one landscape demo video (docs/media/demo.mp4).

Each scene is the phone recording on the left and a short caption on the right. The caption cards are
plain HTML rendered by Playwright, so the text is easy to change.

    python3 docs/record_demo.py && python3 docs/make_video.py
"""

import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

MEDIA = Path(__file__).parent / "media"
WORK = MEDIA / "raw" / "video"
CHROMIUM = "/opt/pw-browsers/chromium"
W, H = 1920, 1080
PHONE_H = 960  # the recording is scaled to this height and placed on the left
PHONE_X, PHONE_Y = 250, 60

SCENES = [
    ("01-start-walk", "1 · Tell it how you're arriving",
     "Gemma (gemma4:31b, open weights) writes three challenges for the next half hour, fitted to the "
     "weather, the light that is left and what you wrote.",
     "In production this takes 1.3–1.9 s."),
    ("02-tell-and-swap", "2 · Answer by telling",
     "Write it, record a voice note (ElevenLabs turns it into text you can edit) or take a photo that "
     "Gemma checks. Don't fancy one? Swap it.",
     "The green dot means a model wrote it; grey, the hand-written backup."),
    ("03-finish-walk", "3 · Close the walk",
     "Real minutes, kilometres and a few words. Stickers unlock as you go.",
     "Everything is optional: it's your notebook."),
    ("04-progress", "4 · See it add up",
     "Your week, your year, and a notebook of 67 stickers, each showing how far you are.",
     "History shown here is demo data."),
    ("05-sky", "The sky follows your local hour",
     "Morning, sunset, night: the start screen is drawn for the time it is where you are.",
     ""),
]

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:%(W)dpx;height:%(H)dpx;background:#191e54;font-family:Inter,system-ui,sans-serif;color:#fff;overflow:hidden}
.phone{position:absolute;left:%(px)dpx;top:%(py)dpx;width:%(pw)dpx;height:%(ph)dpx;border-radius:44px;background:#0b0e2e;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.text{position:absolute;left:%(tx)dpx;right:140px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:28px}
h1{font-size:64px;line-height:1.05;margin:0;letter-spacing:-.02em;font-weight:800}
p{font-size:34px;line-height:1.4;margin:0;color:#dcdaf5;max-width:900px}
small{font-size:26px;color:#ffb300;font-weight:600}
.brand{position:absolute;right:140px;bottom:56px;font-size:24px;color:#a9a6d6;font-weight:600}
.center{left:0;right:0;text-align:center;align-items:center}
</style></head><body>%(body)s</body></html>"""


def card(page, path, body, phone=True):
    pw = round(PHONE_H * 780 / 1688)
    html = CARD % {"W": W, "H": H, "px": PHONE_X - 14, "py": PHONE_Y - 14, "pw": pw + 28, "ph": PHONE_H + 28,
                   "tx": PHONE_X + pw + 120, "body": ('<div class="phone"></div>' if phone else "") + body}
    page.set_content(html)
    page.screenshot(path=str(path))


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    # The sky GIF becomes a clip like the others.
    run("-i", str(MEDIA / "05-sky-through-the-day.gif"), "-vf", "scale=780:-2,pad=780:1688:0:(oh-ih)/2:color=#f5f4f8,fps=24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(WORK / "05-sky.mp4"))

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": W, "height": H})
        card(page, WORK / "title.png", """<div class="text center">
            <h1 style="font-size:96px">MicroAdventures</h1>
            <p style="font-size:40px;max-width:1300px">Tiny walking challenges, written by an open-weight model,<br>to get you out of the house for half an hour.</p>
            <small>Hacktoberfest 2026 · Open-Source AI Challenge · “Touch Grass”</small></div>""", phone=False)
        card(page, WORK / "end.png", """<div class="text center">
            <h1 style="font-size:80px">Try it outside</h1>
            <p style="font-size:42px">micro-adventure.onrender.com</p>
            <p style="font-size:32px">github.com/antoniahp/micro-adventure</p>
            <small>Gemma · Render · ElevenLabs · MongoDB Atlas · Sentry</small></div>""", phone=False)
        for name, title, text, note in SCENES:
            card(page, WORK / f"{name}.png", f"""<div class="text"><h1>{title}</h1><p>{text}</p>
                {f'<small>{note}</small>' if note else ''}</div><div class="brand">MicroAdventures</div>""")
        browser.close()

    parts = []
    for still, seconds in (("title", 3.5), ("end", 4)):
        run("-loop", "1", "-t", str(seconds), "-i", str(WORK / f"{still}.png"), "-vf", "fps=24,format=yuv420p",
            "-c:v", "libx264", str(WORK / f"{still}.mp4"))
    parts.append(WORK / "title.mp4")
    for name, *_ in SCENES:
        clip = WORK / "05-sky.mp4" if name == "05-sky" else MEDIA / f"{name}.mp4"
        out = WORK / f"scene-{name}.mp4"
        run("-loop", "1", "-i", str(WORK / f"{name}.png"), "-i", str(clip),
            "-filter_complex", f"[1:v]scale=-2:{PHONE_H}[v];[0:v][v]overlay={PHONE_X}:{PHONE_Y}:shortest=1,fps=24,format=yuv420p",
            "-c:v", "libx264", "-crf", "20", str(out))
        parts.append(out)
    parts.append(WORK / "end.mp4")
    (WORK / "list.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run("-f", "concat", "-safe", "0", "-i", str(WORK / "list.txt"), "-c:v", "libx264", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(MEDIA / "demo.mp4"))
    print(MEDIA / "demo.mp4")


if __name__ == "__main__":
    main()
