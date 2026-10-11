"""Records the GIFs for the DEV post by driving the real web client with Playwright.

The frontend is the real build (`npm run build`, served by `vite preview`). The backend is replaced by a
small in-memory stand-in so the recording is repeatable and does not write to production, but every
challenge it hands out is one that Gemma (gemma4:31b on Ollama Cloud) actually wrote for the live app,
copied from production on 11 Oct 2026. The history behind the dashboard and the notebook is demo data.

    cd web && npm run build && npx vite preview --port 4180 &
    python3 docs/record_demo.py            # writes docs/media/*.gif and *.mp4
"""

import copy
import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4180"
OUT = Path(__file__).parent / "media"
RAW = OUT / "raw"
CHROMIUM = "/opt/pw-browsers/chromium"
PHONE = {"width": 390, "height": 844}

# Written by gemma4:31b in production on 11 Oct 2026, 00:36 in Madrid (dark), for: calm, 30 min, location shared,
# "Long day of meetings, I want something quiet."
GEMMA_EN = [
    ("nature", "Spot a tree's silhouette against the night sky and describe its shape to me."),
    ("sensory", "Notice the warmth of the sunny day lingering on the pavement and describe the feeling."),
    ("people_watching", "Observe a passerby's pace and tell me if they seem rushed or relaxed."),
]
# Written by gemma4:31b for the same request a minute later: used when a challenge is swapped.
GEMMA_SPARES = {
    "nature": "Spot a tree or plant under the streetlights and describe its shape to me.",
    "people_watching": "Observe someone walking calmly and describe their pace or mood in your own words.",
}
MODEL = "gemma4:31b"
NOTE = "Long day of meetings, I want something quiet."


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class FakeApi:
    """Just enough of the Django API for the screens being recorded."""

    def __init__(self, context, progress_before, progress_after, weekly, yearly):
        self.context = context
        self.progress = progress_before
        self.progress_after = progress_after
        self.weekly = weekly
        self.yearly = yearly
        self.walk = None
        self.user = str(uuid.uuid4())

    def new_walk(self, payload):
        now = datetime.now(timezone.utc)
        self.walk = {
            "id": str(uuid.uuid4()), "user_id": self.user, "mood": payload.get("mood", "calm"),
            "minutes": payload.get("minutes", 30), "weather": payload.get("weather", "sunny"),
            "note": payload.get("note", ""), "language": payload.get("language", "en"), "swaps_used": 0,
            "walked_minutes": None, "distance_km": None, "diary": "", "finished_at": None, "created_at": iso(now),
            "challenges": [
                {"id": str(uuid.uuid4()), "category": c, "text": t, "status": "pending", "accepts_photo": c not in ("people_watching", "sound"),
                 "story": "", "source": MODEL}
                for c, t in GEMMA_EN
            ],
        }
        return self.walk["id"]

    def handle(self, route):
        req = route.request
        path = re.sub(r"^.*?/api", "", req.url.split("?")[0])
        method = req.method

        def ok(body, status=200):
            return route.fulfill(status=status, content_type="application/json", body=json.dumps(body))

        if path.startswith("/auth/"):
            return ok({"access": "demo", "refresh": "demo", "user_id": self.user})
        if path == "/warmup":
            return route.fulfill(status=204)
        if path == "/context":
            return ok(self.context)
        if path == "/walks" and method == "POST":
            return ok({"id": self.new_walk(json.loads(req.post_data or "{}"))}, 201)
        m = re.match(r"^/walks/([^/]+)$", path)
        if m:
            return ok(self.walk)
        m = re.match(r"^/walks/[^/]+/challenges/([^/]+)/(complete|swap)$", path)
        if m:
            challenge = next(c for c in self.walk["challenges"] if c["id"] == m.group(1))
            if m.group(2) == "complete":
                story = re.search(r'name="story"\r\n\r\n(.*?)\r\n--', req.post_data or "", re.S)
                challenge["story"] = story.group(1) if story else ""
                challenge["status"] = "completed"
            else:
                challenge["text"] = GEMMA_SPARES[challenge["category"]]
                challenge["id"] = str(uuid.uuid4())
                self.walk["swaps_used"] += 1
            return route.fulfill(status=204)
        if path.endswith("/finish"):
            data = json.loads(req.post_data or "{}")
            self.walk.update(walked_minutes=data.get("walked_minutes"), distance_km=data.get("distance_km"),
                             diary=data.get("diary", ""), finished_at=iso(datetime.now(timezone.utc)))
            self.progress = self.progress_after
            return route.fulfill(status=204)
        if path.endswith("/progress"):
            return ok(self.progress)
        if "/summary/weekly" in path:
            return ok(self.weekly)
        if "/summary/yearly" in path:
            return ok(self.yearly)
        if path.endswith("/reminders"):
            return ok({"enabled": True, "weekday_time": "18:30", "weekend_time": "11:00", "timezone": "Europe/Madrid",
                       "language": "en", "telegram_connected": True, "has_place": True, "telegram_available": True})
        if path.endswith("/account"):
            return ok({"nickname": "Antonia", "google_linked": False})
        return ok({})


# Every sticker in production (code, family, goal), in the order the notebook shows them.
STICKERS = [
    ("walks_3", "walks", 3), ("five_walks", "walks", 5), ("walks_10", "walks", 10), ("twenty_walks", "walks", 20),
    ("walks_30", "walks", 30), ("walks_50", "walks", 50), ("walks_75", "walks", 75), ("walks_100", "walks", 100),
    ("first_walk", "challenges", 1), ("challenges_10", "challenges", 10), ("challenges_25", "challenges", 25),
    ("fifty_challenges", "challenges", 50), ("challenges_100", "challenges", 100), ("challenges_150", "challenges", 150),
    ("challenges_250", "challenges", 250), ("challenges_500", "challenges", 500),
    ("perfect_walk", "perfect", 1), ("perfect_3", "perfect", 3), ("perfect_5", "perfect", 5), ("perfect_10", "perfect", 10), ("perfect_25", "perfect", 25),
    ("streak_2", "streak", 2), ("streak_3", "streak", 3), ("streak_5", "streak", 5), ("streak_7", "streak", 7),
    ("streak_10", "streak", 10), ("streak_14", "streak", 14), ("streak_30", "streak", 30),
    ("km_5", "km", 5), ("ten_km", "km", 10), ("km_25", "km", 25), ("km_50", "km", 50), ("km_100", "km", 100), ("km_200", "km", 200),
    ("minutes_60", "minutes", 60), ("five_hours", "minutes", 300), ("minutes_600", "minutes", 600),
    ("minutes_1200", "minutes", 1200), ("minutes_3000", "minutes", 3000),
    ("stories_5", "stories", 5), ("storyteller", "stories", 10), ("stories_15", "stories", 15), ("stories_20", "stories", 20),
    ("stories_35", "stories", 35), ("stories_50", "stories", 50),
    ("photos_1", "photos", 1), ("photos_5", "photos", 5), ("photos_15", "photos", 15), ("photos_30", "photos", 30), ("photos_50", "photos", 50),
    ("categories_3", "categories", 3), ("all_categories", "categories", 5),
    *[(f"{cat}_{goal}", cat, goal) for cat in ("sensory", "sound", "culture", "nature", "people_watching") for goal in (5, 15, 30)],
]


def sticker_book(**current):
    book = [{"code": code, "family": family, "current": current[family], "goal": goal, "unlocked": current[family] >= goal}
            for code, family, goal in STICKERS]
    return {"walks_count": current["walks"], "days_walked": current["walks"], "challenges_completed": current["challenges"],
            "perfect_walks": current["perfect"], "stickers": [s["code"] for s in book if s["unlocked"]], "sticker_book": book,
            "current_streak": current["streak"]}


def demo_data(context):
    common = dict(perfect=3, streak=4, km=17.0, photos=2, categories=5, culture=3, people_watching=2)
    before = sticker_book(walks=9, challenges=27, minutes=290, stories=10, sensory=5, sound=6, nature=4, **common)
    # This walk adds three challenges, 35 minutes and a story: it unlocks "10 walks", "5 hours outdoors" and "Friend of the woods I".
    after = sticker_book(walks=10, challenges=30, minutes=325, stories=11, sensory=6, sound=6, nature=5, **{**common, "km": 19.4, "people_watching": 3})
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    days = [{"day": (monday + timedelta(days=i)).strftime("%Y-%m-%d"), "walks": w, "challenges": c}
            for i, (w, c) in enumerate([(1, 3), (0, 0), (1, 2), (1, 3), (1, 3), (0, 0), (0, 0)])]
    weekly = {"week_start": days[0]["day"], "week_end": days[-1]["day"], "walks_count": 4, "days_walked": 4,
              "challenges_completed": 11, "perfect_walks": 2, "minutes": 140, "km": 8.6, "stories": 4, "days": days,
              "moods": {"tired": 1, "calm": 2, "active": 1}, "categories": {"sound": 3, "nature": 3, "sensory": 2, "culture": 2, "people_watching": 1},
              "previous_walks": 2, "previous_challenges": 5, "previous_minutes": 70, "previous_km": 4.1,
              "feeling": 4, "feeling_note": ""}
    months = [{"month": m, "walks": w, "challenges": c, "minutes": mi, "km": k, "feeling": f}
              for m, w, c, mi, k, f in [(1, 0, 0, 0, 0, None), (2, 0, 0, 0, 0, None), (3, 0, 0, 0, 0, None), (4, 0, 0, 0, 0, None),
                                         (5, 0, 0, 0, 0, None), (6, 0, 0, 0, 0, None), (7, 0, 0, 0, 0, None), (8, 0, 0, 0, 0, None),
                                         (9, 0, 0, 0, 0, None), (10, 10, 30, 325, 19.4, 4), (11, 0, 0, 0, 0, None), (12, 0, 0, 0, 0, None)]]
    yearly = {"year": today.year, "years": [today.year], "walks_count": 10, "days_walked": 10, "challenges_completed": 30,
              "perfect_walks": 3, "minutes": 325, "km": 19.4, "stories": 11, "longest_streak": 5, "best_month": 10, "months": months,
              "moods": {"tired": 2, "calm": 5, "active": 3}, "categories": {"sound": 6, "nature": 5, "sensory": 5, "culture": 3, "people_watching": 2},
              "weekdays": [2, 1, 2, 2, 2, 0, 1]}
    return before, after, weekly, yearly


def to_gif(video, name, start=0.0, end=None, fps=10, width=340):
    """Trims the recording and turns it into a small looping GIF (palette per clip, so colours stay true)."""
    trim = ["-ss", f"{start}"] + (["-to", f"{end}"] if end else [])
    gif = OUT / f"{name}.gif"
    filters = f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *trim, "-i", str(video), "-vf", filters, str(gif)], check=True)
    mp4 = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *trim, "-i", str(video), "-vf", "scale=780:-2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)], check=True)
    return gif


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(RAW, ignore_errors=True)
    context = json.loads((OUT / "context.json").read_text())
    before, after, weekly, yearly = demo_data(context)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)

        def scene(name, hour, run, lang="en"):
            api = FakeApi(context, copy.deepcopy(before), copy.deepcopy(after), weekly, yearly)
            # Videos are recorded at CSS-pixel size, so a 390 px phone would come out blurry. The window is twice
            # that and the page is zoomed 2x: same layout as a 390 px phone, recorded at 780 x 1688.
            ctx = browser.new_context(viewport={"width": PHONE["width"] * 2, "height": PHONE["height"] * 2}, device_scale_factor=1,
                                      record_video_dir=str(RAW / name), record_video_size={"width": 780, "height": 1688},
                                      geolocation={"latitude": 40.4168, "longitude": -3.7038}, permissions=["geolocation"],
                                      locale="en-GB", timezone_id="Europe/Madrid")
            ctx.add_init_script(f"localStorage.setItem('lang','{lang}');"
                                "document.addEventListener('DOMContentLoaded',()=>{document.documentElement.style.zoom='2'});")
            ctx.route("**/api/**", api.handle)
            page = ctx.new_page()
            page.goto(f"{BASE}/?hour={hour}")
            page.wait_for_timeout(900)
            marks = run(page, api) or {}
            page.wait_for_timeout(600)
            video = page.video.path()
            ctx.close()
            return Path(video), marks

        # 1. Start a walk: note, length, weather from the real forecast, and Gemma's challenges.
        def start(page, api):
            page.get_by_role("button", name=re.compile("weather", re.I)).first.click()
            page.wait_for_timeout(1200)
            box = page.locator("textarea#note")
            box.click()
            page.keyboard.type(NOTE, delay=45)
            page.wait_for_timeout(500)
            page.mouse.wheel(0, 600)
            page.wait_for_timeout(900)
            page.get_by_role("button", name="Get my walk ready").click()
            page.wait_for_timeout(1500)  # production takes 1.3-1.9 s to write three challenges
            page.get_by_text(GEMMA_EN[0][1]).wait_for()
            page.wait_for_timeout(2600)

        # 2. Tell a challenge, then swap one Gemma wrote.
        def tell(page, api):
            page.get_by_role("button", name="Get my walk ready").click()
            page.get_by_text(GEMMA_EN[0][1]).wait_for()
            page.wait_for_timeout(900)
            page.get_by_role("button", name="Tell it").first.click()
            page.wait_for_timeout(500)
            page.get_by_role("textbox", name="Your answer").click()
            page.keyboard.type("A plane tree, all knots and long arms, black against the last bit of orange sky.", delay=32)
            page.wait_for_timeout(500)
            page.get_by_role("button", name="Send").click()
            page.wait_for_timeout(1700)
            page.get_by_role("button", name=re.compile(r"^Swap")).nth(1).click()
            page.wait_for_timeout(2400)

        # 3. Finish the walk: real minutes, km and a few words; a sticker is unlocked.
        def finish(page, api):
            page.get_by_role("button", name="Get my walk ready").click()
            page.get_by_text(GEMMA_EN[0][1]).wait_for()
            for i, story in enumerate(["A plane tree, all knots and long arms, against the sky.",
                                       "The stone bench by the library was still warm. Nice surprise.",
                                       "A man with a dog, walking slower than the dog wanted. Relaxed."]):
                page.get_by_role("button", name="Tell it").first.click()
                page.get_by_role("textbox", name="Your answer").fill(story)
                page.get_by_role("button", name="Send").click()
                page.wait_for_timeout(700)
            page.wait_for_timeout(1400)
            page.get_by_role("button", name="Tell my walk").click()
            page.wait_for_timeout(600)
            page.locator("#walked-minutes").click()
            page.keyboard.type("35", delay=90)
            page.locator("#walked-km").click()
            page.keyboard.type("2,4", delay=90)
            page.locator("#walk-diary").click()
            page.keyboard.type("Left my laptop at the office and took the long way round the park.", delay=30)
            page.wait_for_timeout(400)
            page.get_by_role("button", name="Save my walk").click()
            page.wait_for_timeout(3200)

        # 4. Dashboard (week and year) and the notebook of stickers.
        def progress(page, api):
            page.get_by_role("button", name="Dashboard").click()
            page.wait_for_timeout(1800)
            page.mouse.wheel(0, 700)
            page.wait_for_timeout(1400)
            page.mouse.wheel(0, -700)
            page.wait_for_timeout(500)
            page.get_by_role("button", name="Year").click()
            page.wait_for_timeout(1800)
            page.get_by_role("button", name="Notebook").click()
            page.wait_for_timeout(1500)
            for _ in range(4):
                page.mouse.wheel(0, 420)
                page.wait_for_timeout(700)
            page.wait_for_timeout(600)

        clips = {}
        clips["01-start-walk"] = scene("start", 20.2, start)
        clips["02-tell-and-swap"] = scene("tell", 20.2, tell)
        clips["03-finish-walk"] = scene("finish", 20.6, finish)
        clips["04-progress"] = scene("progress", 12, progress)
        browser.close()

    starts = {"01-start-walk": 0.4, "02-tell-and-swap": 1.4, "03-finish-walk": 1.4, "04-progress": 0.6}
    for name, (video, _) in clips.items():
        gif = to_gif(video, name, start=starts[name])
        print(f"{gif.name}: {gif.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
