from uberlytics.model import models

def get_pretty_user_stats(user):
    user_stats, uber_trips = get_user_stats(user)
    return [
        'You\'ve taken %s trips' % user_stats['total_trips'],
        'You\'ve spent %s hours in ubers' % round(float(user_stats['total_duration']) / 3600),
        'You\'ve travelled a total of %s miles' % user_stats['total_distance'],
        'You\'ve spent $%s' % (float(user_stats['total_subtotal']) / 100),
        'Your longest trip was %s miles' % user_stats['longest_trip'].distance,
        'Your shorest trip was %s miles' % user_stats['shortest_trip'].distance,
        'Your most expensive trip was $%s' % (float(user_stats['priciest_trip'].subtotal) / 100),
        'Your cheapest trip was $%s' % (float(user_stats['cheapest_trip'].subtotal) / 100),]


def get_user_stats(user):
    uber_trips = models.UberTrip.select().where(models.UberTrip.user_id == user.user_id)
    uber_stats = {}
    i = 0
    longest_trip = None
    shortest_trip = None
    priciest_trip = None
    cheapest_trip = None
    first_trip_date = None

    hour_counts = {}
    day_counts = {}
    car_counts = {}

    for trip in uber_trips:
        if not longest_trip or trip.distance > longest_trip.distance:
            longest_trip = trip
        if trip.distance > 0 and (not shortest_trip or
                                  trip.distance < shortest_trip.distance):
            shortest_trip = trip
        if not priciest_trip or trip.subtotal > priciest_trip.subtotal:
            priciest_trip = trip
        if trip.subtotal > 0 and (not cheapest_trip or
                                  trip.subtotal < cheapest_trip.subtotal):
            cheapest_trip = trip
        if not first_trip_date or trip.date < first_trip_date:
            first_trip_date = trip.date
        # tally totals.
        for attr in ('subtotal', 'distance', 'duration'):
            total_key = 'total_%s' % attr
            uber_stats[total_key] = uber_stats.setdefault(total_key, 0) + getattr(trip, attr)
        car_counts[trip.car_type] = car_counts.get(trip.car_type, 0) + 1

        day = trip.date.strftime('%A')
        day_counts[day] = day_counts.get(day, 0) + 1

        i += 1

    uber_stats['cheapest_trip'] = cheapest_trip
    uber_stats['priciest_trip'] = priciest_trip
    uber_stats['longest_trip'] = longest_trip
    uber_stats['shortest_trip'] = shortest_trip
    uber_stats['total_trips'] = i
    uber_stats['car_counts'] = car_counts
    uber_stats['day_counts'] = day_counts
    uber_stats['first_trip_date'] = first_trip_date

    return uber_stats, uber_trips
