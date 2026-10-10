from collections import Counter
from datetime import date, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from microadventures.domain.models.walk import Walk


def zone_or_utc(name: str | None) -> tzinfo:
    """The person's time zone, or UTC when it is missing or unknown: a summary is never refused for that."""
    try:
        return ZoneInfo(name or "UTC")
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


class WalkHistory:
    """What a person has done, read in their own time zone. Every summary and sticker counts with it."""

    def __init__(self, walks: list[Walk], zone: tzinfo):
        self.walks = list(walks)
        self.zone = zone

    def day_of(self, walk: Walk) -> date:
        return walk.created_at.astimezone(self.zone).date()

    def between(self, start: date, end: date) -> "WalkHistory":
        """The walks from start up to, but not including, end."""
        return WalkHistory([w for w in self.walks if start <= self.day_of(w) < end], self.zone)

    @property
    def walks_count(self) -> int:
        return len(self.walks)

    @property
    def walks_with_progress(self) -> list[Walk]:
        return [w for w in self.walks if any(c.is_completed for c in w.challenges)]

    @property
    def active_days(self) -> set[date]:
        return {self.day_of(w) for w in self.walks_with_progress}

    @property
    def challenges_completed(self) -> int:
        return sum(1 for w in self.walks for c in w.challenges if c.is_completed)

    @property
    def perfect_walks(self) -> int:
        return sum(1 for w in self.walks if w.is_perfect)

    @property
    def minutes(self) -> int:
        """Only what people said they walked; many leave it empty."""
        return sum(w.walked_minutes or 0 for w in self.walks)

    @property
    def km(self) -> float:
        return round(sum(w.distance_km or 0 for w in self.walks), 1)

    @property
    def stories(self) -> int:
        told = sum(1 for w in self.walks for c in w.challenges if c.is_completed and c.story.strip())
        return told + sum(1 for w in self.walks if w.diary.strip())

    @property
    def photos(self) -> int:
        return sum(1 for w in self.walks for c in w.challenges if c.is_completed and c.with_photo)

    @property
    def categories(self) -> Counter:
        return Counter(str(c.category) for w in self.walks for c in w.challenges if c.is_completed)

    @property
    def moods(self) -> Counter:
        return Counter(str(w.mood) for w in self.walks)

    def walks_per_weekday(self) -> list[int]:
        counts = [0] * 7
        for walk in self.walks:
            counts[self.day_of(walk).weekday()] += 1
        return counts

    def longest_streak(self) -> int:
        """The most days in a row with at least one completed challenge."""
        best = run = 0
        previous = None
        for day in sorted(self.active_days):
            run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
            best = max(best, run)
            previous = day
        return best

    def current_streak(self, today: date) -> int:
        """Days in a row up to today (or up to yesterday, while today is still open)."""
        days = self.active_days
        day = today if today in days else today - timedelta(days=1)
        run = 0
        while day in days:
            run += 1
            day -= timedelta(days=1)
        return run

    def metrics(self) -> dict[str, int]:
        return {
            "walks": self.walks_count,
            "challenges": self.challenges_completed,
            "perfect_walks": self.perfect_walks,
            "categories": len(self.categories),
            "streak": self.longest_streak(),
            "stories": self.stories,
            "photos": self.photos,
            "km": int(self.km),
            "minutes": self.minutes,
            **{f"category_{category}": count for category, count in self.categories.items()},
        }
