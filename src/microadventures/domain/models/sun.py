import math
from datetime import date, datetime, timedelta, timezone

J2000 = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)


def sun_times(latitude: float, longitude: float, day: date) -> tuple[datetime, datetime]:
    """Sunrise and sunset (UTC) at a place, from the standard sunrise equation. Good to a couple of minutes.

    It is the backup for weather services that do not say when the sun sets. Near the poles the sun may not set
    (the whole day is light) or not rise (the whole day is dark); then the two times bracket or collapse the day.
    """
    noon = datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc)
    n = round((noon - J2000).total_seconds() / 86400)
    mean_solar_time = n - longitude / 360
    anomaly = math.radians((357.5291 + 0.98560028 * mean_solar_time) % 360)
    center = 1.9148 * math.sin(anomaly) + 0.02 * math.sin(2 * anomaly) + 0.0003 * math.sin(3 * anomaly)
    ecliptic_longitude = math.radians((math.degrees(anomaly) + center + 180 + 102.9372) % 360)
    transit = mean_solar_time + 0.0053 * math.sin(anomaly) - 0.0069 * math.sin(2 * ecliptic_longitude)
    declination = math.asin(math.sin(ecliptic_longitude) * math.sin(math.radians(23.4397)))

    latitude_rad = math.radians(latitude)
    cos_hour_angle = (math.sin(math.radians(-0.833)) - math.sin(latitude_rad) * math.sin(declination)) / (
        math.cos(latitude_rad) * math.cos(declination)
    )
    midnight = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    if cos_hour_angle > 1:  # polar night
        moment = J2000 + timedelta(days=transit)
        return moment, moment
    if cos_hour_angle < -1:  # midnight sun
        return midnight, midnight + timedelta(days=1)
    hour_angle_days = math.degrees(math.acos(cos_hour_angle)) / 360
    return J2000 + timedelta(days=transit - hour_angle_days), J2000 + timedelta(days=transit + hour_angle_days)
