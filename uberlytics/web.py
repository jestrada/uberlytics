import locale
locale.setlocale(locale.LC_ALL, '')

from flask import abort
from flask import Flask
from flask import g
from flask import request
from flask import render_template
from flask import session
from flask import url_for

from jinja2 import Markup

from uberlytics.lib import stats
from uberlytics.model import models

app = Flask(__name__)
app.debug = True

@app.route('/')
def stats_view():
    # just show stats for the single user in the db for now

    email = request.args.get('email')
    email = email.strip()
    try:
        user = models.User.get(models.User.email == email)
    except models.User.DoesNotExist:
        abort(404)
    user_stats, uber_trips = stats.get_user_stats(user)
    p_stats = []

    first_date = user_stats['first_trip_date'].strftime('%B %Y')
    p_stats.append(Markup('You\'ve taken <strong>%s</strong> trips since %s' % (user_stats['total_trips'], first_date)))
    p_stats.append(Markup('You\'ve spent <strong>%i</strong> hours in ubers' % round(float(user_stats['total_duration']) / 3600)))
    p_stats.append(Markup('You\'ve travelled a total of <strong>%s</strong> miles' % user_stats['total_distance']))
    p_stats.append(Markup('You\'ve spent <strong>%s</strong>' % locale.currency(float(user_stats['total_subtotal']) / 100, grouping=True)))

    p_stats.append((
         Markup('Your longest trip was <strong>%s</strong> miles' % user_stats['longest_trip'].distance),
         user_stats['longest_trip']))

    p_stats.append((
        Markup('Your shortest trip was <strong>%s</strong> miles' % user_stats['shortest_trip'].distance),
        user_stats['shortest_trip']))
    p_stats.append((
        Markup('Your most expensive trip was <strong>%s</strong>' % locale.currency(float(user_stats['priciest_trip'].subtotal) / 100, grouping=True)),
        user_stats['priciest_trip']))
    p_stats.append((
        Markup('Your cheapest trip was <strong>%s</strong>' % locale.currency(float(user_stats['cheapest_trip'].subtotal) / 100, grouping=True)),
        user_stats['cheapest_trip']))

    # todo pass in all the trip paths to draw polylines.
    coordinates = []
    trip_paths = []
    for trip in uber_trips:
        trip_coordinates = trip.get_trip_coordinates()
        if not trip_coordinates:
            continue
        trip_paths.append(trip_coordinates)
        #coordinates.extend(trip.get_trip_coordinates())

    return render_template('stats.html', printable_stats=p_stats, trip_paths=trip_paths)

if __name__ == '__main__':
    app.run()
    models.init()
