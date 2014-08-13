from datetime import datetime
import requests
import json
import re

from lxml import html

from uberlytics.model import models

def login(email, password):
    """ Authenticates with Uber given an email and password.
    """

    login = requests.get('https://www.uber.com/log-in', verify=False)
    cookies = login.cookies
    login_tree = html.fromstring(login.text)
    csrf_token = login_tree.xpath('//input[@name="x-csrf-token"]')[0].get('value')

    data = {
        'x-csrf-token': csrf_token,
        'login': email,
        'password': password, }
    login = requests.post('https://www.uber.com/log-in', cookies=cookies, data=data, verify=False)
    user_id = login.cookies['user_id']
    login_via_token_url = json.loads(login.text)['redirect_to']
    login_via_token = requests.get(login_via_token_url, cookies=cookies, verify=False)
    cookies = login_via_token.cookies
    return (user_id, cookies['session'], cookies['session.sig'])

def update_ride_history(user):
    i = 1
    trip_ids = []
    # get all trip ids by walking through the trip pages.
    paginate = True
    cookies = {
        'session': user.session_key,
        'session.sig': user.session_sig }
    while paginate:
        trips_response = requests.get('https://riders.uber.com/trips?page=%s' % i, cookies=cookies, verify=False)
        trips_tree = html.fromstring(trips_response.text)
        trip_details = trips_tree.xpath('//tr[contains(@class, "trip-expand__origin")]')
        # stop paginating once we have reached the end.
        if not len(trip_details):
            break

        print 'adding %s trip ids' % len(trip_details)
        # parse out trip ids and stop paginating once an existing trip is reached.
        for trip in trip_details:
            trip_id = trip.get("data-target").split('-')[1]
            trip_exists = models.UberTrip.select().where(models.UberTrip.trip_id==trip_id).count()
            if trip_exists:
                paginate = False
                break
            trip_ids.append(trip_id)

        i += 1

    print 'downloading %s trips' % len(trip_ids)
    # store trips by oldest first in case there's an error while looping through the trips.
    trip_ids.reverse()
    for trip_id in trip_ids:
        trip_exists = models.UberTrip.select().where(models.UberTrip.trip_id==trip_id).count()
        if trip_exists:
            print 'trip %s already exists' % trip_id
            continue

        print 'req %s' % trip_id
        trip_details_response = requests.get('https://riders.uber.com/trips/%s' % trip_id, cookies=cookies, verify=False)
        trip_tree = html.fromstring(trip_details_response.text)

        # parse out the trip date
        page_lead = trip_tree.xpath('//div[@class="page-lead"]')[0].text_content()
        date_text = page_lead.replace('Your Trip', '')
        trip_date = datetime.strptime(date_text, '%H:%M %p on %B %d %Y')

        # parse out the trip subtotal
        fare_table = trip_tree.xpath('//table[contains(@class, "fare-breakdown")]')[0]

        charged_row = fare_table.xpath('.//tr')[-1]
        subtotal_text = charged_row.xpath('.//td')[-1].text_content()[1:]
        subtotal = int(100 * float(subtotal_text))

        surge_rate = 0
        surge_tr = fare_table.xpath('.//tr[contains(@class, "fare-breakdown__surge")]')
        if surge_tr:
            surge_tr = surge_tr[0]
            surge_text = surge_tr.getchildren()[0].text_content()
            surge_text = surge_text.replace('Surge x', '')
            surge_rate = int(100 * float(surge_text))

        # parse out the trip address
        trip_addresses = trip_tree.xpath('//div[contains(@class, "trip-address")]')
        start_address = trip_addresses[0]
        start_address = start_address.xpath('.//h6')[0].text_content()

        end_address = trip_addresses[2]
        end_address = end_address.xpath('.//h6')[0].text_content()

        # parse out the car type, distane, and trip time
        trip_details = trip_tree.xpath('//div[contains(@class, "flexbox color--neutral")]')
        car_div, distance_div, duration_div = trip_details[0].xpath('.//div[contains(@class, "flexbox__item")]')
        car_type = car_div.xpath('.//h5')[0].text_content()
        distance = float(distance_div.xpath('.//h5')[0].text_content())
        duration_text = duration_div.xpath('.//h5')[0].text_content()
        hours, minutes, seconds = map(int, duration_text.split(':'))
        duration = seconds + (minutes * 60) + (hours * 3600)

        # parse out the map image src
        map_img = trip_tree.xpath('//img[contains(@class, "img--full img--flush")]')[0]
        map_img_src = map_img.get('src')
        map_components = map_img_src.split("&")
        start_lat, start_long, end_lat, end_long = [''] * 4
        for c in map_components:
            if 'dot-start' in c:
                start_lat, start_long = re.findall(r'(-?\d+\.\d+)', c)
            elif 'dot-finish' in c:
                end_lat, end_long = re.findall(r'(-?\d+\.\d+)', c)

        print 'sav %s' % trip_id
        models.UberTrip.create(
            trip_id=trip_id,
            user_id=user.user_id,
            date=trip_date,
            duration=duration,
            subtotal=subtotal,
            surge_rate=surge_rate,
            map_img_src=map_img_src,
            start_address=start_address,
            end_address=end_address,
            start_lat=start_lat,
            start_long=start_long,
            end_lat=end_lat,
            end_long=end_long,
            car_type=car_type,
            distance=distance)

