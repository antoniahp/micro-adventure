import pytest
import requests

from microadventures.domain.exceptions.weather_unavailable_exception import WeatherUnavailableException
from microadventures.domain.models.reminder_card import ReminderCard
from microadventures.domain.models.weather import Sky
from microadventures.infrastructure.api.open_meteo_weather_service import OpenMeteoWeatherService
from microadventures.infrastructure.api.telegram_notification_sender import TelegramNotificationSender

ANSWER = {
    "utc_offset_seconds": 7200,
    "current": {"temperature_2m": 17.4, "precipitation": 0.0, "weather_code": 2, "wind_speed_10m": 11.2},
    "daily": {"sunrise": ["2026-10-09T07:50"], "sunset": ["2026-10-09T19:42"]},
}


class FakeGet:
    def __init__(self, body=None, error=None, status_code=200):
        self.body, self.error, self.status_code = body or ANSWER, error, status_code
        self.calls = []

    def get(self, url, params, timeout, headers=None):
        self.calls.append((url, params))
        if self.error:
            raise self.error
        return self

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(str(self.status_code), response=self)

    def json(self):
        return self.body


def test_it_reads_the_weather_and_the_sun_of_the_place():
    weather = OpenMeteoWeatherService(http=FakeGet()).at(40.4168, -3.7038)

    assert (weather.temperature_c, weather.sky, weather.wind_kmh) == (17.4, Sky.CLOUDY, 11.2)
    assert weather.sunset.isoformat() == "2026-10-09T19:42:00+02:00"  # local time of the place, with its offset


def test_it_asks_for_a_rounded_place_and_remembers_the_answer_for_a_while():
    http, now = FakeGet(), [0.0]
    service = OpenMeteoWeatherService(http=http, clock=lambda: now[0])

    service.at(40.4168, -3.7038)
    service.at(40.4201, -3.7001)  # the same kilometre
    assert len(http.calls) == 1 and http.calls[0][1]["latitude"] == 40.42

    now[0] = 1801
    service.at(40.4168, -3.7038)
    assert len(http.calls) == 2


@pytest.mark.parametrize("http", [FakeGet(error=requests.Timeout("slow")), FakeGet(status_code=500), FakeGet(body={"nothing": 1})])
def test_any_failure_becomes_weather_unavailable(http):
    with pytest.raises(WeatherUnavailableException):
        OpenMeteoWeatherService(http=http).at(40.4, -3.7)


# --- the Telegram card ---

class FakePost:
    def __init__(self, fail_first=False):
        self.fail_first, self.requests = fail_first, []
        self.status_code = 200

    def post(self, url, json, timeout):
        self.requests.append((url, json))
        self.status_code = 400 if self.fail_first and len(self.requests) == 1 else 200
        return self


CARD = ReminderCard("https://x/reminder-weekday.png", "<b>Hola</b>", "🚶 Salir", "https://x", "⏰ En 1 hora", "😴 Hoy no")


def test_the_card_is_a_photo_with_a_caption_and_three_buttons():
    http = FakePost()

    TelegramNotificationSender("123:TOKEN", http=http).send_card("555", CARD)

    url, body = http.requests[0]
    assert url.endswith("/sendPhoto") and body["photo"] == CARD.photo_url and body["parse_mode"] == "HTML"
    rows = body["reply_markup"]["inline_keyboard"]
    assert rows[0] == [{"text": "🚶 Salir", "url": "https://x"}]
    assert [button["callback_data"] for button in rows[1]] == ["snooze", "skip"]


def test_if_telegram_cannot_use_the_picture_the_same_message_goes_out_without_it():
    http = FakePost(fail_first=True)

    TelegramNotificationSender("123:TOKEN", http=http).send_card("555", CARD)

    assert [url.rsplit("/", 1)[1] for url, _ in http.requests] == ["sendPhoto", "sendMessage"]
    assert http.requests[1][1]["text"] == "<b>Hola</b>" and "reply_markup" in http.requests[1][1]


def test_without_an_address_the_open_button_is_left_out():
    http = FakePost()
    card = ReminderCard("", "x", "Open", "", "Later", "No")

    TelegramNotificationSender("123:TOKEN", http=http).send_card("555", card)

    assert len(http.requests[0][1]["reply_markup"]["inline_keyboard"]) == 1  # only the row with "in 1 hour" and "not today"


def test_a_button_press_is_answered_and_the_webhook_asks_for_button_presses():
    http = FakePost()
    sender = TelegramNotificationSender("123:TOKEN", http=http)

    sender.answer("cb-1", "Vale")
    sender.register("https://x/hook", "s")

    assert http.requests[0][0].endswith("/answerCallbackQuery") and http.requests[0][1] == {"callback_query_id": "cb-1", "text": "Vale"}
    assert http.requests[1][1]["allowed_updates"] == ["message", "callback_query"]


def test_a_429_is_remembered_for_five_minutes_so_the_service_is_left_alone():
    http, now = FakeGet(status_code=429), [0.0]
    service = OpenMeteoWeatherService(http=http, clock=lambda: now[0])

    for _ in range(3):
        with pytest.raises(WeatherUnavailableException, match="429"):
            service.at(40.4, -3.7)
    assert len(http.calls) == 1

    now[0] = 301
    with pytest.raises(WeatherUnavailableException):
        service.at(40.4, -3.7)
    assert len(http.calls) == 2
