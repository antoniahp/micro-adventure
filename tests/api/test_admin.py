from django.test import Client


def test_admin_login_page_is_served():
    response = Client().get("/admin/login/")

    assert response.status_code == 200
