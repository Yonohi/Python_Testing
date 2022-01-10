import pytest
from flask import request
from ..fixtures import client, competitions, clubs, old_competitions
from Python_Testing import server
from server import POINTS_PER_PLACE


def test_client(client):
    client.get('/?email=a@a')
    assert request.args['email'] == 'a@a'


def test_index_status_code_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_wrong_email(client, mocker, clubs):
    mocker.patch.object(server, 'clubs', clubs)
    response = client.post('/showSummary', data=dict(email='a@a'), follow_redirects=True)
    message = "Sorry, that email wasn't found.".replace("'", "&#39;")
    assert request.path == '/'
    assert response.status_code == 200
    assert message in response.data.decode()


def test_good_email(client, mocker, clubs):
    mocker.patch.object(server, 'clubs', clubs)
    response = client.post('/showSummary', data=dict(email='test@test'), follow_redirects=True)
    # Comment: we can use b"" for message and remove .decode for response.data
    message = "Sorry, that email wasn't found.".replace("'", "&#39;")
    assert request.path == '/showSummary'
    assert response.status_code == 200
    assert message not in response.data.decode()


def test_book_ok(mocker, client, clubs, competitions):
    mocker.patch.object(server, 'clubs', clubs)
    mocker.patch.object(server, 'competitions', competitions)
    response = client.get('/book/' +
                          competitions[0]['name'] +
                          '/' + clubs[0]['name'])
    message = 'Booking available!'
    assert message in response.data.decode()
    assert request.path == '/book/Test Comp+12/Test Club+12'


def test_old_book(mocker, client, clubs, old_competitions):
    mocker.patch.object(server, 'clubs', clubs)
    mocker.patch.object(server, 'competitions', old_competitions)
    response = client.get('/book/' +
                          old_competitions[0]['name'] +
                          '/' + clubs[0]['name'])
    message = 'Sorry this competition is too old.'
    assert message in response.data.decode()
    assert request.path == '/book/Test Comp/Test Club+12'


# 3 catégories pour réaliser tout les tests:
#               1) club et comp > 12
#               2) club < 12 et comp >12
#               3) club < 12, comp < 12 et club > comp
@pytest.mark.parametrize("points", [-1, 0, 1, 6, 7, 8, 9, 12, 13])
def test_purchase_places(mocker, points, client, competitions, clubs):
    mocker.patch.object(server, 'competitions', competitions)
    mocker.patch.object(server, 'clubs', clubs)

    # 1) club et comp > 12
    if points in [-1, 0, 1, 7, 12, 13]:
        response = client.post('/purchasePlaces',
                               data=dict(places=points,
                                         competition='Test Comp+12',
                                         club='Test Club+12'),
                               follow_redirects=True)

        # test strictement positif
        if points in [-1, 0]:
            message = "Test Club+12 can't use this number of points." \
                      f" Number available: {25 * POINTS_PER_PLACE}".replace("'", "&#39;")
            assert message in response.data.decode()
            assert int(clubs[0]['points']) == 25 * POINTS_PER_PLACE
            assert int(competitions[0]['numberOfPlaces']) == 25

        # 13 (12+1)
        elif points in [13]:
            message = "A club can't book more than 12 places.".replace("'", "&#39;")
            assert message in response.data.decode()
            assert int(clubs[0]['points']) == 25 * POINTS_PER_PLACE
            assert int(competitions[0]['numberOfPlaces']) == 25

        # test nb ok
        elif points in [1, 7, 12]:
            message = 'Great-booking complete!'
            assert message in response.data.decode()
            if points == 1:
                assert int(clubs[0]['points']) == 24 * POINTS_PER_PLACE
                assert int(competitions[0]['numberOfPlaces']) == 24

    # test succession de demande > 12 (2*7 à l'aide du test précédent)
    if points in [7]:
        response = client.post('/purchasePlaces',
                               data=dict(places=points,
                                         competition='Test Comp+12',
                                         club='Test Club+12'),
                               follow_redirects=True)
        message = "A club can't book more than 12 places.".replace("'",
                                                                   "&#39;")
        assert message in response.data.decode()
        if points == 7:
            assert int(clubs[0]['points']) == 18 * POINTS_PER_PLACE
            assert int(competitions[0]['numberOfPlaces']) == 18

    # 2) club < 12 et comp >12
    if points in [8, 9]:
        # remarque: le club testé à plus de points que la competition
        response = client.post('/purchasePlaces',
                               data=dict(places=points,
                                         competition='Test Comp+12',
                                         club='Test Club-12'),
                               follow_redirects=True)
        # test max points club
        if points in [8]:
            message = "Great-booking complete!"
            assert message in response.data.decode()
            assert int(clubs[1]['points']) == 0 * POINTS_PER_PLACE
            assert int(competitions[0]['numberOfPlaces']) == 17
        # test max+1
        elif points in [9]:
            message = "Test Club-12 can't use this number of points." \
                      f" Number available: {8 * POINTS_PER_PLACE}".replace("'", "&#39;")
            assert message in response.data.decode()
            assert int(clubs[1]['points']) == 8 * POINTS_PER_PLACE
            assert int(competitions[0]['numberOfPlaces']) == 25

    # 3) club < 12, comp < 12 et club > comp
    if points in [6]:
        # remarque: le club testé à plus de points que la competition
        response = client.post('/purchasePlaces',
                               data=dict(places=points,
                                         competition='Test Comp-12',
                                         club='Test Club-12'),
                               follow_redirects=True)
        # test nb dépassant le nb de points pour la compet
        if points in [6]:
            message = "The number requested is greater than the number of " \
                      "places available."
            assert message in response.data.decode()
            assert int(clubs[1]['points']) == 8 * POINTS_PER_PLACE
            assert int(competitions[1]['numberOfPlaces']) == 5


def test_purchase_places_no_value(mocker, client, competitions, clubs):
    mocker.patch.object(server, 'competitions', competitions)
    mocker.patch.object(server, 'clubs', clubs)
    try:
        client.post('/purchasePlaces',
                    data=dict(places='',
                              competition='Test Comp+12',
                              club='Test Club+12'),
                    follow_redirects=True)
    except ValueError:
        assert True


def test_date_is_ok(competitions):
    result = server.date_is_ok(competitions[0])
    assert result == True


def test_date_is_not_ok(competitions):
    result = server.date_is_ok(competitions[2])
    assert result == False


def test_display(client):
    response = client.get('/pointsDisplay')
    assert response.status_code == 200
    assert 'Points Display' in response.data.decode()


def test_logout(client):
    client.get('/logout', follow_redirects=True)
    assert request.path == '/'
