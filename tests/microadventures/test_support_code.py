import re

from microadventures.domain.models.support_code import normalize, support_code


def test_the_code_is_short_readable_and_always_the_same_for_an_id():
    code = support_code("5f0a8c1e-1111-4222-8333-944455556666")

    assert re.fullmatch(r"MA-[2-9A-HJKMNP-TV-Z]{4}-[2-9A-HJKMNP-TV-Z]{4}", code)
    assert support_code("5f0a8c1e-1111-4222-8333-944455556666") == code


def test_different_ids_get_different_codes():
    codes = {support_code(f"user-{n}") for n in range(5000)}

    assert len(codes) == 5000


def test_a_code_written_by_hand_is_understood():
    code = support_code("user-1")
    bare = code.replace("-", "").lower()

    assert normalize(bare) == code
    assert normalize(bare[2:]) == code
    assert normalize(f"  {code.lower()} ") == code
