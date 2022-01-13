from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
import json
import pytest
from unittest import mock
from django.test import Client

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
# from commons.utils.token_generator import id_generator
from users.models import CustomUser
from django.contrib.auth.models import Group
# from commons.utils.token_generator import id_generator
from django.conf import settings
authenticationRequired= True if settings.AUTHENTICATION_REQUIRED == "True" else False

@pytest.fixture()
def setup_user(db):
    """sets up a user to be used for login"""
    user = CustomUser.objects.create_superuser("admin@domain.com", "admin")
    user.status = "Active"
    user.is_active = True
    user.name = "Sachin"
    user.save()

def test_authenticate_get(setup_user, client):
    """ tests authenticate_get """
    path = reverse("login")
    client.login(email="admin@domain.com", password="admin")
    response = client.get(path)
    assert response.json()["success"] == (True and authenticationRequired)

def test_authenticate_post(setup_user, client):
    """ tests authenticate_post """
    path = reverse("login")
    data = {"email": "admin@domain.com", "password": "admin"}
    response = client.post(path, data=json.dumps(data), content_type="application/json")
    assert response.json()["success"] == True
    data = {"email": "random@cuebook.ai", "password": "random"}
    response = client.post(path, data=json.dumps(data), content_type="application/json")
    assert response.json()["success"] == False

# @pytest.mark.django_db(transaction=True)
def test_auth_middleware(setup_user, client):
    """ test middleware """
    c = Client()
    res = c.post("/accounts/login", {"email": "admin@domain.com", "password": "admin"} , follow=True)
    res.status_code == 200
    res = c.get("/accounts/login", follow=True)
    assert res.status_code == 200
    path = reverse("connections")
    res = c.get(path)
    assert res.status_code == 200