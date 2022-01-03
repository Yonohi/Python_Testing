import json
import re
import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def date_is_ok(competition):
    list_time_comp = re.split(r'[-: ]+', competition['date'])
    year = int(list_time_comp[0])
    month = int(list_time_comp[1])
    day = int(list_time_comp[2])
    hour = int(list_time_comp[3])
    min = int(list_time_comp[4])
    comp_datetime = datetime.datetime(year=year,
                                      month=month,
                                      day=day,
                                      hour=hour,
                                      minute=min)
    today = datetime.datetime.today()
    if today < comp_datetime:
        return True
    else:
        return False

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions,
                               clubs=clubs)
    except IndexError:
        flash("Sorry, that email wasn't found.", 'error')
        return redirect('/')


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        if date_is_ok(foundCompetition):
            flash('Booking available!')
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("Sorry this competition is too old.", 'error')
            return render_template('welcome.html', club=foundClub,
                                   competitions=competitions, clubs=clubs)
    else:
        flash("Something went wrong-please try again", 'error')
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    # test places correctes pour le nombre de points du clubs
    if 0 < placesRequired <= int(club['points']):
        try :
            nb_points = int(competition[f"{club['name']}"])
        except KeyError:
            competition[f"{club['name']}"] = 0
            nb_points = int(competition[f"{club['name']}"])
        if 0 < placesRequired <= 12 and\
                0 < placesRequired <= (12 - nb_points):
            # test nombre ne dépassant pas le nombre de places dispo
            if placesRequired <= int(competition['numberOfPlaces']):
                competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
                club['points'] = int(club['points']) - placesRequired
                competition[f"{club['name']}"] += placesRequired
                flash('Great-booking complete!')
                return render_template('welcome.html', club=club,
                                       competitions=competitions, clubs=clubs)
            else:
                flash("The number requested is greater than the number of "
                      "places available.", 'error')
                return book(competition['name'],club['name'])
        else:
            flash("A club can't book more than 12 places.", 'error')
            return book(competition['name'], club['name'])
    else:
        flash(f"{club['name']} can't use this number of points."
              f" Number available: {club['points']}", 'error')
        return book(competition['name'],club['name'])

# TODO: Add route for points display
@app.route('/pointsDisplay')
def pointsDisplay():
    return render_template('points_board.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

