"""The YouTube cut, "A day and a night with MicroAdventures", narrated: the daytime Telegram nudges, what's new
(the guide, the privacy notice, deleting an account), a real night walk, and photos of friends and family trying
it. Writes docs/media/day-and-night.mp4 (1920x1080, with voice).

    pip install playwright kokoro-onnx soundfile
    python3 docs/make_full_video.py <folder with kokoro-v1.0.onnx and voices-v1.0.bin>

Each scene lasts as long as its line takes to say, plus a short breath: recordings are sped up (or held on their
last frame) to fit. The voice is placed using the real length of every rendered scene, so it can't drift.
The voice is Kokoro (open weights, Apache 2.0), made on this machine. Inputs live in docs/media/raw/full/ (not
committed). Only photos where nobody's face, no card and no street sign can be read are used; recordings are cut
so no contact list and no other app's icon shows.
"""

import base64
import hashlib
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import sync_playwright

MEDIA = Path(__file__).parent / "media"
RAW = MEDIA / "raw" / "full"
WORK = RAW / "build"
VOICES = RAW / "voice"
CHROMIUM = "/opt/pw-browsers/chromium"
W, H, FPS = 1920, 1080, 30
PHONE_H = 960
PHONE_X, PHONE_Y = 260, 60
PHONE_W = round(PHONE_H * 1080 / 2400)
VOICE, VOICE_SPEED = "af_heart", 1.08
LEAD, BREATH = 0.25, 0.55  # silence before a line, and after it before the next cut
MAX_SPEED = 4  # faster than this, a screen recording can't be followed


@dataclass
class Scene:
    line: str  # what the voice says
    kind: str  # "card" (a still), "photos" (a still that drifts in) or "phone" (recordings in the phone frame)
    body: str = ""  # the card's HTML
    clips: list[tuple[str, float, float]] = field(default_factory=list)  # (recording, start s, end s) for "phone"
    min_seconds: float = 2.5
    maxw: str = "560px"


def data_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


STYLE = """<style>
html,body{margin:0;width:1920px;height:1080px;background:#191e54;font-family:Inter,system-ui,sans-serif;color:#fff;overflow:hidden}
.phone{position:absolute;left:%(px)dpx;top:%(py)dpx;width:%(pw)dpx;height:%(ph)dpx;border-radius:44px;background:#0b0e2e;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.text{position:absolute;left:%(tx)dpx;right:140px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:28px}
h1{font-size:62px;line-height:1.05;margin:0;letter-spacing:-.02em;font-weight:800}
p{font-size:34px;line-height:1.4;margin:0;color:#dcdaf5;max-width:960px}
small{font-size:26px;color:#ffb300;font-weight:600}
.brand{position:absolute;right:140px;bottom:56px;font-size:24px;color:#a9a6d6;font-weight:600}
.tag{position:absolute;right:140px;top:56px;font-size:22px;font-weight:700;letter-spacing:.04em}
.bg{position:absolute;inset:-60px;background-size:cover;background-position:center;filter:blur(40px) brightness(.45)}
.photos{position:absolute;inset:0;display:flex;gap:28px;justify-content:center;align-items:center;padding-bottom:150px}
.photos img{max-height:820px;max-width:%(maxw)s;border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.5);object-fit:cover}
.caption{position:absolute;left:0;right:0;bottom:56px;text-align:center}
.caption h1{font-size:54px}.caption p{margin:10px auto 0;font-size:32px;max-width:1500px}
.center{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:24px;padding:0 160px}
</style>"""


def page_html(body: str, maxw: str) -> str:
    return "<!doctype html><html><head><meta charset='utf-8'>" + STYLE % {
        "px": PHONE_X - 14, "py": PHONE_Y - 14, "pw": PHONE_W + 28, "ph": PHONE_H + 28,
        "tx": PHONE_X + PHONE_W + 120, "maxw": maxw} + f"</head><body>{body}</body></html>"


def phone_card(title: str, text: str, note: str = "", tag: str = "● REAL PHONE", colour: str = "#10a878") -> str:
    return (f'<div class="phone"></div><div class="tag" style="color:{colour}">{tag}</div>'
            f'<div class="text"><h1>{title}</h1><p>{text}</p>{f"<small>{note}</small>" if note else ""}</div>'
            f'<div class="brand">MicroAdventures</div>')


def new_card(title: str, text: str) -> str:
    return phone_card(title, text, tag="● NEW TODAY", colour="#ffb300")


def night_card(title: str, text: str) -> str:
    return phone_card(title, text, tag="● REAL WALK")


def photo_card(photos: list[str], title: str, text: str) -> str:
    images = "".join(f'<img src="{data_uri(RAW / p)}">' for p in photos)
    return (f'<div class="bg" style="background-image:url({data_uri(RAW / photos[0])})"></div>'
            f'<div class="photos">{images}</div><div class="caption"><h1>{title}</h1><p>{text}</p></div>')


def center(kicker: str, title: str, text: str, size: int = 96, background: str = "") -> str:
    return (background + f'<div class="center"><small style="font-size:28px">{kicker}</small>'
            f'<h1 style="font-size:{size}px">{title}</h1><p style="font-size:38px;max-width:1300px">{text}</p></div>')


def scenes() -> list[Scene]:
    title_bg = f'<div class="bg" style="background-image:url({data_uri(RAW / "p-title.jpg")});filter:blur(6px) brightness(.38)"></div>'
    return [
        Scene("A day and a night with MicroAdventures, on real streets.", "photos", center(
            "REAL PHONES · REAL STREETS · MALLORCA", "A day and a night with MicroAdventures",
            "Three tiny challenges for the time you have, the light that's left and how you feel, written by Gemma, "
            "an open-weight model.", 92, title_bg)),
        Scene("At half past eleven, Telegram nudges me: seven hours of light left. Not now? I tap: in one hour.", "phone",
              phone_card("11:31 · The nudge, by day", "“Good time to head out. 7 h 43 min of light left · 22 °C, cloudy.” "
                         "Not now? “In 1 hour.”", "Telegram bot · weather from Open-Meteo"),
              [("v-day-nudge.mp4", 3.25, 16.2)]),
        Scene("An hour later, it's back, with the light and the weather updated.", "phone",
              phone_card("12:40 · One hour later", "From the home screen into Telegram: the nudge is back, updated. "
                         "6 h 35 min of light, 24 °C."),
              [("v-day-later.mp4", 1.0, 3.3), ("v-day-later.mp4", 4.9, 11.6)]),
        Scene("And the sky in the app follows the day, all the way to sunset.", "card",
              f'<div class="photos" style="padding-bottom:170px"><img src="{data_uri(RAW / "s-morning.jpg")}" style="border-radius:36px">'
              f'<img src="{data_uri(RAW / "s-evening.jpg")}" style="border-radius:36px"></div>'
              '<div class="caption"><h1>The sky follows the day</h1><p>11:29: 7 h 44 min of light. 18:41: 35 minutes left, '
              'sunset at 19:16, and the illustration turns to dusk.</p></div>', maxw="420px"),
        Scene("New today: open it from the home screen, and a short guide shows you around. The terms are accepted "
              "right where you start.", "phone",
              new_card("New · A short guide", "Five bubbles explain the tabs the first time, and three more the buttons "
                       "of your first walk. The terms are accepted by starting, with the notice right above the button."),
              [("v-new-es.mp4", 1.8, 3.4), ("v-new-es.mp4", 13, 34)]),
        Scene("A privacy policy in plain words, built for Europe's GDPR. No cookies, no tracking.", "phone",
              new_card("New · Privacy, in plain words", "A privacy policy and terms in English and Spanish, written for "
                       "the EU's GDPR. No cookies, no tracking, no ads; even the fonts come from our own server."),
              [("v-new-en.mp4", 6, 26)]),
        Scene("And you can delete everything, for good, in two taps.", "phone",
              new_card("New · Delete my account", "Walks, stories, reminders and the Google link go, for good, in two "
                       "taps. A short code to quote if you ever write about your data."),
              [("v-new-es.mp4", 3.5, 12)]),
        Scene("Then it got dark.", "card", center("LATER THAT EVENING", "Then it got dark 🌙",
                                                 "Same app, same village: a real night walk, start to finish."), min_seconds=2.2),
        Scene("At the hour I picked, Telegram nudges me: it's dark and sixteen degrees, so keep to lit streets.", "phone",
              night_card("1 · The nudge", "“Hi Antonia 👋 Good time to head out. It's already dark · 16 °C, clear. "
                         "Better a short walk on lit streets.”"), [("n-redmi.mp4", 5.5, 13.5)]),
        Scene("I tell the app I'm a bit tired, but good. It knows it's night, so Gemma writes three small challenges "
              "for lit, busy streets.", "phone",
              night_card("2 · How are you arriving?", "“A bit tired but good.” The app already knows it's dark and "
                         "16 °C, so Gemma writes challenges for lit, busy streets."), [("n-redmi-2.mp4", 6, 56)]),
        Scene("I answer one with a photo. Gemma's vision checks it: a plant under a streetlamp. Accepted.", "phone",
              night_card("3 · Answer with a photo", "Gemma's vision checks the photo against the challenge. "
                         "A plant under a streetlamp: accepted."), [("n-redmi-2.mp4", 58, 90)]),
        Scene("But it's strict. Asked for a lit shop window, I try some stone steps, and Gemma calls it out.", "phone",
              night_card("4 · …and it's strict", "“A lit sign or shop window”, and I try some stone steps. Gemma: "
                         "“some stone steps and a shadow, there's no lit sign.” Fair. 😅"), [("n-redmi-2.mp4", 116, 150)]),
        Scene("Too cold to type? Just say it. The voice note becomes text, and the audio is never stored.", "phone",
              night_card("5 · Or just say it", "A voice note, turned into text by ElevenLabs. You can still edit it "
                         "before sending, and the audio is never stored."), [("n-redmi.mp4", 158, 205)]),
        Scene("Same walk on an iPhone, in English. I mention dinner, and a challenge asks me to listen for a sound "
              "that reminds me of it.", "phone",
              night_card("6 · Same walk, iPhone 16, English", "A note about dinner becomes “listen for a sound that "
                         "reminds you of your dinner.” A streetlight photo: accepted."), [("n-iphone.mp4", 25, 72)]),
        Scene("Answer of the night: I can hear some chickens moving around.", "phone",
              night_card("Answer of the night", "“I can hear some chickens moving around 😂🙈”"), [("n-iphone.mp4", 75, 99)]),
        Scene("Switch language mid-walk: the challenges you have stay, new ones arrive in English.", "phone",
              night_card("7 · Change language mid-walk", "The challenges you already have keep their language; new ones "
                         "come in English."), [("n-iphone-lang.mp4", 45, 53)]),
        Scene("Ten minutes, a quarter of a kilometre, and a few words about a quiet, lit-up village. A perfect walk.", "phone",
              night_card("8 · Close the walk", "10 minutes, 0.25 km and a few words: “I loved getting out at night and "
                         "seeing there's life in the village.” No swaps: a perfect walk."), [("n-redmi.mp4", 255, 285)]),
        Scene("It all adds up: a new sticker, a notebook with sixty-seven to collect, and the week on the dashboard.", "phone",
              night_card("9 · It adds up", "A sticker unlocked, the notebook of 67 stickers and the week on the "
                         "dashboard."), [("n-redmi-2.mp4", 232, 262)]),
        Scene("Then we tried it with friends and family.", "photos",
              photo_card(["p-two-phones.jpg"], "We tried it for real", "Friends and family, this afternoon: Android in "
                         "Spanish, iPhone in English."), maxw="1500px"),
        Scene("Any phone, any language. Nothing to install.", "photos",
              photo_card(["p-street.jpg", "p-grass-en.jpg"], "Same app, any phone", "A web app you can add to the home "
                         "screen.")),
        Scene("They answered their way, typed or out loud, and closed the walk with a few words.", "photos",
              photo_card(["p-challenge.jpg", "p-voice.jpg", "p-keypad.jpg"], "Answer your way",
                         "“Listen for a pleasant sound and tell me what it makes you feel.” Typed, or said out loud."),
              maxw="500px"),
        Scene("Three walks. Three perfect walks.", "photos",
              photo_card(["p-done-5.jpg", "p-done-10.jpg", "p-done-14.jpg"], "Three walks, three “perfect walks”",
                         "3/3 challenges, no swaps: 5, 10 and 14 minutes. First badges unlocked."), maxw="500px"),
        Scene("Thank you for watching, and thanks to everyone who walked with us today.", "card", center(
            "HACKTOBERFEST 2026 · TOUCH GRASS", "Thank you 💛",
            "To my friends and family for walking with me today, and to you for watching.<br><br>"
            "<span style='font-size:34px;color:#ffb300'>micro-adventure.onrender.com</span><br>"
            "<span style='font-size:28px;color:#a9a6d6'>github.com/antoniahp/micro-adventure · Gemma · Render · "
            "ElevenLabs · MongoDB Atlas · Sentry</span>", 110), min_seconds=5),
    ]


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def seconds_of(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout)


def voice(kokoro, line: str) -> Path:
    """The line spoken, cached by its text so changing one line only re-records that one."""
    import soundfile

    path = VOICES / f"{hashlib.sha1(f'{VOICE}{VOICE_SPEED}{line}'.encode()).hexdigest()[:12]}.wav"
    if not path.exists():
        samples, rate = kokoro.create(line, voice=VOICE, speed=VOICE_SPEED, lang="en-us")
        soundfile.write(path, samples, rate)
    return path


def still(png: Path, seconds: float, out: Path, drift: bool):
    frames = round(seconds * FPS)
    vf = (f"scale={W * 6 // 5}:{H * 6 // 5},zoompan=z='1+0.05*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p") if drift else f"fps={FPS},format=yuv420p"
    run("-loop", "1", "-framerate", str(FPS), "-t", f"{seconds}", "-i", str(png), "-vf", vf, "-frames:v", str(frames),
        "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", str(out))


def phone(card: Path, clips: list[tuple[str, float, float]], seconds: float, out: Path):
    """The recordings, back to back and sped up together to last `seconds` (held on the last frame if short)."""
    total = sum(end - start for _, start, end in clips)
    speed = max(total / seconds, 0.85)
    inputs, chains = [], []
    for i, (name, start, end) in enumerate(clips):
        inputs += ["-ss", str(start), "-t", str(end - start), "-i", str(RAW / name)]
        chains.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{speed},scale={PHONE_W}:{PHONE_H}:force_original_aspect_ratio=decrease,"
                      f"pad={PHONE_W}:{PHONE_H}:(ow-iw)/2:(oh-ih)/2:color=#0b0e2e,fps={FPS},setsar=1[c{i}]")
    n = len(clips)
    joined = "".join(f"[c{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0," if n > 1 else "[c0]"
    graph = ";".join(chains) + f";{joined}tpad=stop_mode=clone:stop_duration=30[v];" + \
        f"[{n}:v][v]overlay={PHONE_X}:{PHONE_Y},fps={FPS},format=yuv420p"
    run(*inputs, "-loop", "1", "-framerate", str(FPS), "-i", str(card), "-filter_complex", graph,
        "-frames:v", str(round(seconds * FPS)), "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "20",
        "-preset", "veryfast", str(out))


def main(models: Path):
    from kokoro_onnx import Kokoro

    WORK.mkdir(parents=True, exist_ok=True)
    VOICES.mkdir(parents=True, exist_ok=True)
    kokoro = Kokoro(str(models / "kokoro-v1.0.onnx"), str(models / "voices-v1.0.bin"))
    plan = scenes()
    lines = [voice(kokoro, s.line) for s in plan]

    parts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, (scene, line) in enumerate(zip(plan, lines)):
            seconds = max(scene.min_seconds, LEAD + seconds_of(line) + BREATH)
            if scene.kind == "phone":
                seconds = max(seconds, sum(end - start for _, start, end in scene.clips) / MAX_SPEED)
            seconds = round(seconds * FPS) / FPS
            png, out = WORK / f"s{i:02d}.png", WORK / f"s{i:02d}.mp4"
            page.set_content(page_html(scene.body, scene.maxw))
            page.wait_for_timeout(150)
            page.screenshot(path=str(png))
            if scene.kind == "phone":
                phone(png, scene.clips, seconds, out)
            else:
                still(png, seconds, out, drift=scene.kind == "photos")
            parts.append(out)
            print(f"{i:02d} {seconds:5.2f}s  {scene.line[:70]}", flush=True)
        browser.close()

    # The voice track is built from the real length of every rendered scene, so line N starts exactly with scene N.
    starts, at = [], 0.0
    for part in parts:
        starts.append(at)
        at += seconds_of(part)
    inputs, chains = [], []
    for i, (line, start) in enumerate(zip(lines, starts)):
        inputs += ["-i", str(line)]
        delay = round((start + LEAD) * 1000)
        chains.append(f"[{i}:a]aresample=44100,adelay={delay}|{delay}[a{i}]")
    audio = WORK / "voice.m4a"
    run(*inputs, "-filter_complex", ";".join(chains) + ";" + "".join(f"[a{i}]" for i in range(len(lines))) +
        f"amix=inputs={len(lines)}:normalize=0,loudnorm=I=-16:TP=-1.5,apad=whole_dur={at:.3f}[a]",
        "-map", "[a]", "-t", f"{at:.3f}", "-c:a", "aac", "-b:a", "160k", str(audio))

    (WORK / "list.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    out = MEDIA / "day-and-night.mp4"
    run("-f", "concat", "-safe", "0", "-i", str(WORK / "list.txt"), "-i", str(audio), "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(out))
    print(out, f"{seconds_of(out):.1f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
