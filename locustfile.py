from locust import HttpUser, task
from server import loadClubs, loadCompetitions


class ProjectPerfTest(HttpUser):
    clubs = loadClubs()
    competitions = loadCompetitions()
    club = clubs[0]
    competition = competitions[0]

    @task
    def get_home(self):
        self.client.get("/")

    @task
    def get_points_display(self):
        self.client.get('/pointsDisplay')

    @task
    def post_for_login(self):
        self.client.post('/showSummary', data=dict(email=self.club['email']))

    @task
    def get_book(self):
        self.client.get('/book/' +
                        self.competition['name'] +
                        '/' + self.club['name'])

    @task
    def post_places(self):
        self.client.post('/purchasePlaces',
                         {'club': self.club['name'],
                          'competition': self.competition['name'],
                          'places': 1})

    @task
    def get_logout(self):
        self.client.get('/logout')
