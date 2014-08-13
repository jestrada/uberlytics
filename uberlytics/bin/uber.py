import sys
from datetime import datetime
import getpass

from uberlytics.model import models
from uberlytics.lib import uber
from uberlytics.lib import stats

def update_history():
    print 'uber login'
    models.init()

    email = raw_input('enter your email:')
    email = email.strip()
    # check for an existing user in the db and use the user info from the entry if one exists.
    try:
        user = models.User.get(models.User.email == email)
        user_id = user.user_id
        session_key = user.session_key
        session_sig = user.session_sig
    except:
        password = getpass.getpass('enter your password:')
        user_id, session_key, session_sig = uber.login(email, password)

    # create a user object if one does not exist.
    user = None
    try:
        user = models.User.get(models.User.user_id == user_id)
        user.session_key = session_key
        user.session_sig = session_sig
        user.update_date = datetime.utcnow()
        user.save()
    except models.User.DoesNotExist:
        # create a new user.
        user = models.User.create(
            user_id=user_id,
            email=email,
            session_key=session_key,
            session_sig=session_sig,
            update_date=datetime.utcnow())

    uber.update_ride_history(user)

def print_stats():
    email = raw_input('enter your email:')
    email = email.strip()
    print 'uber stats for %s' % email
    try:
        user = models.User.get(models.User.email == email)
    except models.User.DoesNotExist:
        print 'user not found, is "%s" correct' % email

    uber_stats = stats.get_pretty_user_stats(user)
    for stat in uber_stats:
        print stat

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'print_stats':
        print_stats()
    else:
        update_history()
