import hashlib

# 30 symbols with no 0/O, 1/I/L or U: a code read aloud or copied by hand can't be mistaken.
ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"
LENGTH = 8  # 30^8 ≈ 6.6·10^11 codes


def support_code(user_id: str) -> str:
    """A short code the person can quote in an email ("MA-7K3F-9Q2X") instead of their long id.

    It's derived from the id, so nothing new is stored and it never changes; it can't be turned back into the id,
    and at this app's size two people sharing one is practically impossible. `python src/manage.py
    find_support_code MA-XXXX-XXXX` finds the account that owns a code.
    """
    number = int.from_bytes(hashlib.sha256(user_id.encode()).digest()[:8], "big")
    chars = []
    for _ in range(LENGTH):
        number, index = divmod(number, len(ALPHABET))
        chars.append(ALPHABET[index])
    code = "".join(chars)
    return f"MA-{code[:4]}-{code[4:]}"


def normalize(code: str) -> str:
    """What the person wrote (any case, with or without dashes or the MA), in the form support_code() writes it."""
    raw = "".join(c for c in code.upper() if c.isalnum())
    if raw.startswith("MA") and len(raw) == LENGTH + 2:
        raw = raw[2:]
    return f"MA-{raw[:4]}-{raw[4:]}"
