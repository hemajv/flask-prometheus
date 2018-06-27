# flask-prometheus
Flask application setup with Prometheus to export metrics

## Building the docker image
```
      docker build . -t flask-prom
```
## Running the container 
```
      docker run -p 5000:5000 flask-prom
```
