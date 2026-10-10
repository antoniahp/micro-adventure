from core.email_hash import hash_email


def test_the_hash_is_not_the_email():
    assert hash_email("jose@gmail.com") != "jose@gmail.com"
    assert "jose" not in hash_email("jose@gmail.com")
    assert "gmail" not in hash_email("jose@gmail.com")


def test_the_same_email_always_hashes_the_same_way():
    assert hash_email("jose@gmail.com") == hash_email("jose@gmail.com")


def test_it_is_not_case_or_whitespace_sensitive():
    assert hash_email("Jose@Gmail.com") == hash_email(" jose@gmail.com ")


def test_different_emails_hash_differently():
    assert hash_email("jose@gmail.com") != hash_email("maria@gmail.com")
