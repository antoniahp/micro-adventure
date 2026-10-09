import pytest

from microadventures.domain.models.walk_length import WalkLength


@pytest.mark.parametrize(
    "minutes, minimum, maximum, default",
    [(15, 3, 3, 3), (30, 3, 3, 3), (44, 3, 3, 3), (45, 5, 5, 5), (59, 5, 5, 5), (60, 6, 10, 6), (120, 6, 10, 6)],
)
def test_the_number_of_challenges_depends_on_the_time(minutes, minimum, maximum, default):
    length = WalkLength.for_minutes(minutes)

    assert (length.minimum, length.maximum, length.default) == (minimum, maximum, default)


def test_only_the_short_walks_ask_for_simple_challenges():
    assert WalkLength.for_minutes(30).is_short
    assert not WalkLength.for_minutes(45).is_short
    assert not WalkLength.for_minutes(60).is_short


def test_it_accepts_only_numbers_inside_its_range():
    length = WalkLength.for_minutes(90)

    assert [n for n in range(0, 13) if length.accepts(n)] == [6, 7, 8, 9, 10]
