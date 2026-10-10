from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.sticker import CATALOG, sticker_book


def test_the_notebook_has_more_than_fifty_stickers_and_none_repeats():
    codes = [s.code for s in CATALOG]

    assert len(codes) >= 50 and len(set(codes)) == len(codes)
    assert {"first_walk", "perfect_walk", "five_walks", "streak_7", "ten_km"} <= set(codes)  # the first ones keep their codes


def test_a_category_sticker_counts_only_the_challenges_of_that_category():
    book = {s.code: s for s in sticker_book({"category_nature": 7, "category_sound": 2})}

    assert book["nature_5"].unlocked and not book["nature_15"].unlocked
    assert (book["nature_15"].current, book["nature_15"].goal) == (7, 15)
    assert book["sound_5"].current == 2 and not book["sensory_5"].unlocked


def test_every_sticker_says_what_it_is_about():
    families = {s.family for s in CATALOG}

    assert {"walks", "challenges", "streak", "km", "minutes", "stories", "nature"} <= families


def test_only_the_challenges_that_can_be_seen_accept_a_photo():
    accepts = {category: Challenge(category=category, text="x").accepts_photo for category in ChallengeCategory}

    assert accepts == {
        ChallengeCategory.SENSORY: True,
        ChallengeCategory.CULTURE: True,
        ChallengeCategory.NATURE: True,
        ChallengeCategory.SOUND: False,
        ChallengeCategory.PEOPLE_WATCHING: False,
    }
