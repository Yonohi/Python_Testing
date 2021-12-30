import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


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
                               competitions=competitions)
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return redirect('/')


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


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
                                       competitions=competitions)
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


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
