# What is Uberlytics?
A simple little python app that downloads your Uber history and presents useful information back to you.
# How do I use it?
## Install requirements
Run `pip install -p uberlytics/requirements.txt`
## Downloading your Uber data
Once you check out the source, you have to run the uber script which authenticates with Uber on your behalf and proceeds to download your uber history.  To run the script run `python uberlytics/bin/uber.py` and you'll be prompted for your email and password.  Once you've entered your credentials correctly, subsequent calls will only ask for your email and use the session keys returned in the first authentication request.

After a successful login, the script will proceed to scrape your entire user history and store it in a local sqlite db.

## Viewing your Uber Data
To view your Uber data, simply run the flask app in uberlytics by running `python uberlytics/web.py`.  This will run a local web app that displays your uber stats and a simple heat map of where you've been.  Currently, it centers in SF so you can simply drag to a different location if that's not the city you use Uber in.  The web app is VERY simple, so you'll have to pass in the email of the user you wish to view using 'email' as the parameter name.  Here's an example url, 'http://localhost:5000/?email=uberdata@uber.com'.  Enjoy!


# Pending Visualizations

1. Calendar heat map
2. Weekday heat map
3. Most popular hours
4. Polylines showing uber trip paths

# Feedback
Please let me know what additional visualizations you'd like to see or any other improvements I can make.

# Example
![alt](https://raw.githubusercontent.com/jestrada/uberlytics/master/screenshots/UberHeatMap.png)

![alt](https://raw.githubusercontent.com/jestrada/uberlytics/master/screenshots/UberStats.png)
