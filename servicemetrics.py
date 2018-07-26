import random
import time
import os
import sys
import bz2
import pandas as pd
import argparse
from flask import Flask, render_template_string, abort
from datetime import datetime
from prometheus_client import CollectorRegistry, generate_latest, REGISTRY, Counter, Gauge, Histogram

app = Flask(__name__)
#Parsing the required arguments
parser = argparse.ArgumentParser(description='Service metrics')
parser.add_argument('--file', type=str, help='The filename of predicted values to read from')

args = parser.parse_args()
#Read the JSON file
data = pd.read_json(args.file)

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
data['timestamp'] = data['timestamp'].astype(int64) // 10 ** 9
timestamp = data['timestamp']
timestamp = timestamp.tolist()

#Find the current timestamp
current_time = datetime.now().timestamp()
print("The current time is: \n")
print(current_time)

#converting to np.int64 type
current_time = np.int64(current_time)
#Find the index matching with the current timestamp
index = timestamp.index(current_time)

print("The matching index found:", index)
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
