from builtins import breakpoint
from http import client
from logging import exception
import re
import pytest
from unittest import mock
from django.urls import reverse
import unittest
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from mixer.backend.django import mixer
from dataset.models import Dataset


@pytest.mark.django_db(transaction=True)
def test_getSearchCard(client, mocker):
    """
    Test case for delete global dimension
    """
    # Run all index
    path = reverse("runIndexing")
    response = client.get(path)
    assert response.data["success"] == True
    assert response.status_code == 200
