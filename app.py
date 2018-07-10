import random
import time
import os
import sys
import bz2
import argparse
from flask import Flask, render_template_string, abort
from prometheus_client import generate_latest, REGISTRY, Counter, Gauge, Histogram

app = Flask(__name__)
#Parsing the required arguments
parser = argparse.ArgumentParser(description='Service metrics')
parser.add_argument('--file', type=str, help='The filename of backup data to read from')

args = parser.parse_args()


# A counter to count the total number of HTTP requests
REQUESTS = Counter('http_requests_total', 'Total HTTP Requests (count)', ['method', 'endpoint', 'status_code'])

# A gauge (i.e. goes up and down) to monitor the total number of in progress requests
IN_PROGRESS = Gauge('http_requests_inprogress', 'Number of in progress HTTP requests')

# A histogram to measure the latency of the HTTP requests
TIMINGS = Histogram('http_request_duration_seconds', 'HTTP request latency (seconds)')

# A gauge to count the number of packages newly added
PACKAGES_NEW = Gauge('packages_newly_added', 'Packages newly added')


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

@app.route('/prometheus')
def metrics():
	rootdir = args.file
	for dirs in os.listdir(rootdir):
		if not dirs.endswith("_count") and not dirs.endswith("_sum"):
			for dir2 in os.listdir(rootdir + '/' + dirs):
				if dir2.endswith("bz2"):
					with bz2.open(rootdir + '/' + dirs + '/' + dir2, 'rt') as f:
						text = f.read()
	return render_template_string(text)

@app.route('/metrics')
@IN_PROGRESS.track_inprogress()
@TIMINGS.time()
def display():
	REQUESTS.labels(method='GET', endpoint="/metrics", status_code=200).inc()
	return generate_latest(REGISTRY)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
