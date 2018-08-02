import random
import time
import os
import sys
import bz2
import pandas
import argparse
from flask import Flask, render_template_string, abort
from datetime import datetime
from prometheus_client import CollectorRegistry, generate_latest, REGISTRY, Counter, Gauge, Histogram

# Scheduling stuff
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

app = Flask(__name__)

# def job(current_time):
#     # TODO: Replace this function with model training function and set up the correct IntervalTrigger time
#     print("I'm pretend training the model.......... ",current_time)
#     time.sleep(2)
#
# # Schedular schedules a background job that needs to be run regularly
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=lambda: job(datetime.now()),
#     trigger=IntervalTrigger(seconds=5),# change this to a different interval
#     id='training_job',
#     name='Train Prophet model every day regularly',
#     replace_existing=True)
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

#Parsing the required arguments
parser = argparse.ArgumentParser(description='Service metrics')
parser.add_argument('--file', type=str, help='The filename of predicted values to read from', default="predictions.json")

args = parser.parse_args()
#Read the JSON file
data = pandas.read_json(args.file)
print(data.head())

# modify the DataFrame
data = data.set_index(data['timestamp'])
data = data[~data.index.duplicated()]
data = data.sort_values(by=['timestamp'])

#A gauge set for the predicted values
PREDICTED_VALUES = Gauge('predicted_values', 'Forecasted values from Prophet', ['yhat_lower', 'yhat_upper', 'time_stamp'])

# A counter to count the total number of HTTP requests
REQUESTS = Counter('http_requests_total', 'Total HTTP Requests (count)', ['method', 'endpoint', 'status_code'])

# A gauge (i.e. goes up and down) to monitor the total number of in progress requests
IN_PROGRESS = Gauge('http_requests_inprogress', 'Number of in progress HTTP requests')

# A histogram to measure the latency of the HTTP requests
TIMINGS = Histogram('http_request_duration_seconds', 'HTTP request latency (seconds)')

# A gauge to count the number of packages newly added
PACKAGES_NEW = Gauge('packages_newly_added', 'Packages newly added')

#Store the different columns of the pandas dataframe
yhatupper = data['yhat_upper']
yhatlower = data['yhat_lower']
yhat = data['yhat']
#Converting timestamp to Unix time
print("Data Timestamp: \n",data['timestamp'].head())
timestamp = data['timestamp']
print(data.head())

print(data.tail())

#Find the current timestamp
current_time = datetime.now()
print("The current time is: \n")
print(current_time)

#Find the index matching with the current timestamp
index = data.index.get_loc(current_time, method='nearest')

print("The matching index found:", index, "nearest_timestamp is: ", data.iloc[[index]])
#Set the Gauge with the predicted values of the index found
PREDICTED_VALUES.labels(yhat_lower=yhatlower[index], yhat_upper=yhatupper[index], time_stamp=timestamp[index]).set(yhat[index])

# Standard Flask route stuff.
@app.route('/')
# Helper annotation to measure how long a method takes and save as a histogram metric.
@TIMINGS.time()
# Helper annotation to increment a gauge when entering the method and decrementing when leaving.
@IN_PROGRESS.track_inprogress()
def hello_world():
    REQUESTS.labels(method='GET', endpoint="/", status_code=200).inc()  # Increment the counter
    return 'Hello, World!'


@app.route('/hello/<name>')
@IN_PROGRESS.track_inprogress()
@TIMINGS.time()
def index(name):
    REQUESTS.labels(method='GET', endpoint="/hello/<name>", status_code=200).inc()
    return render_template_string('<b>Hello {{name}}</b>!', name=name)

@app.route('/packages')
def countpkg():
	for i in range(10):
		packages_added = True
		if packages_added:
			PACKAGES_NEW.inc()
	return render_template_string('Counting packages....')

@app.route('/metrics')
def metrics():
	return generate_latest(REGISTRY)

@app.route('/prometheus')
@IN_PROGRESS.track_inprogress()
@TIMINGS.time()
def display():
	REQUESTS.labels(method='GET', endpoint="/metrics", status_code=200).inc()
	return generate_latest(REGISTRY)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    pass
