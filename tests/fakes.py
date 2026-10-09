from copy import deepcopy
from uuid import UUID

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.services.challenge_generator import ChallengeGenerator
from microadventures.domain.exceptions.notification_failed_exception import NotificationFailedException
from microadventures.domain.exceptions.walk_not_found_exception import WalkNotFoundException
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.services.bot_webhook import BotWebhook
from microadventures.domain.services.notification_sender import NotificationSender
from microadventures.domain.services.reminder_service import ReminderService
from microadventures.domain.models.weekly_reflection import WeeklyReflection
from microadventures.domain.services.reflection_service import ReflectionService
from microadventures.domain.models.photo_verdict import PhotoVerdict
from microadventures.domain.services.photo_verifier import PhotoVerifier
from microadventures.domain.services.walk_criteria import WalkCriteria
from microadventures.domain.services.walk_service import WalkService
from microadventures.domain.models.walk import Walk


class InMemoryWalkRepository(WalkService):
    """Stores copies, so a handler that forgets to call save() fails its test."""

    def __init__(self):
        self.walks: dict[UUID, Walk] = {}

    def save(self, walk: Walk) -> None:
        self.walks[walk.id] = deepcopy(walk)

    def find_by_criteria(self, criteria: WalkCriteria) -> list[Walk]:
        walks = self.walks.values()
        if criteria.id is not None:
            walks = [walk for walk in walks if walk.id == criteria.id]
        if criteria.user_id is not None:
            walks = [walk for walk in walks if walk.user_id == criteria.user_id]
        return [deepcopy(walk) for walk in walks]

    def find_or_fail_by_id(self, id: UUID) -> Walk:
        if id not in self.walks:
            raise WalkNotFoundException(id)
        return deepcopy(self.walks[id])


class StubChallengeGenerator(ChallengeGenerator):
    def __init__(self, challenges: list[Challenge]):
        self.challenges = challenges
        self.briefs: list[ChallengeBrief] = []

    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        self.briefs.append(brief)
        return self.challenges


class StubPhotoVerifier(PhotoVerifier):
    def __init__(self, verdict: PhotoVerdict = PhotoVerdict(accepted=True)):
        self.verdict = verdict
        self.verified: list[Challenge] = []

    def verify(self, challenge: Challenge, photo: bytes) -> PhotoVerdict:
        self.verified.append(challenge)
        return self.verdict


class InMemoryReminderRepository(ReminderService):
    def __init__(self):
        self.settings: dict[str, ReminderSettings] = {}

    def save(self, settings: ReminderSettings) -> None:
        self.settings[settings.user_id] = deepcopy(settings)

    def find_by_user_id(self, user_id: str) -> ReminderSettings | None:
        return deepcopy(self.settings.get(user_id))

    def find_by_link_code(self, code: str) -> ReminderSettings | None:
        return next((deepcopy(s) for s in self.settings.values() if code and s.link_code == code), None)

    def find_by_telegram_chat_id(self, chat_id: str) -> ReminderSettings | None:
        return next((deepcopy(s) for s in self.settings.values() if chat_id and s.telegram_chat_id == chat_id), None)

    def find_active(self) -> list[ReminderSettings]:
        return [deepcopy(s) for s in self.settings.values() if s.enabled and s.is_linked]


class SpyNotificationSender(NotificationSender, BotWebhook):
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.sent: list[tuple[str, str]] = []
        self.registered: list[tuple[str, str]] = []

    def send(self, chat_id: str, text: str) -> None:
        if self.fail:
            raise NotificationFailedException("Telegram answered 500")
        self.sent.append((chat_id, text))

    def register(self, url: str, secret: str) -> None:
        self.registered.append((url, secret))


class InMemoryReflectionRepository(ReflectionService):
    def __init__(self):
        self.reflections: list[WeeklyReflection] = []

    def save(self, reflection: WeeklyReflection) -> None:
        self.reflections = [r for r in self.reflections if r.id != reflection.id]
        self.reflections.append(deepcopy(reflection))

    def find_by_week(self, user_id: str, week_start) -> WeeklyReflection | None:
        return next((deepcopy(r) for r in self.reflections if r.user_id == user_id and r.week_start == week_start), None)

    def find_by_user_id(self, user_id: str) -> list[WeeklyReflection]:
        return [deepcopy(r) for r in self.reflections if r.user_id == user_id]
