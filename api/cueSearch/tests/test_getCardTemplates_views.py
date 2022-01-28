from builtins import breakpoint
from http import client
import re
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase, Client
from mixer.backend.django import mixer


@pytest.mark.django_db(transaction=True)
def test_getCardTemplates(client, mocker):
    """
    Test case for get card templates
    """
    path = reverse("getCardTemplate")
    response = client.get(path)
    assert response.data["success"]
    assert response.status_code == 200
