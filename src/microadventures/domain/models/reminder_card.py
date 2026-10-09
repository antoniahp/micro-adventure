from dataclasses import dataclass


@dataclass(frozen=True)
class ReminderCard:
    """What a reminder looks like: a picture, a text with a little formatting (HTML) and three buttons."""

    photo_url: str
    caption: str
    open_label: str
    open_url: str  # empty when the server does not know its own address
    snooze_label: str
    skip_label: str
