from Python_Testing.server import app
import pytest


@pytest.fixture()
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def competitions():
    competitions = [
        # Competition with more than 12 places
        {
            "name": "Test Comp+12",
            "date": "2030-01-01 10:00:00",
            "numberOfPlaces": "25"
        },
        # Competition with less than 12 places
        {
            "name": "Test Comp-12",
            "date": "2030-01-01 10:00:00",
            "numberOfPlaces": "5"
        },
        # Old competition
        {
            "name": "Test Comp-12",
            "date": "2010-01-01 10:00:00",
            "numberOfPlaces": "5"
        }
    ]
    return competitions


@pytest.fixture()
def old_competitions():
    competitions = [
        {
            "name": "Test Comp",
            "date": "2000-01-01 10:00:00",
            "numberOfPlaces": "25"
        }
    ]
    return competitions


@pytest.fixture()
def clubs():
    clubs = [
        {
            "name": "Test Club+12",
            "email": "test@test",
            "points": "25"
        },
        {
            "name": "Test Club-12",
            "email": "test2@test",
            "points": "8"
        }
    ]
    return clubs
