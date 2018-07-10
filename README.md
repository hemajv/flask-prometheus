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

# Running the application on OpenShift
app.yaml is the template file (save it locally on your system) from which we can deploy our flask application (app.py) and have it running on OpenShift. 

## We first create the template
```
      oc create -f app.yaml
```
## We then create a new application using this template
```
      oc new-app <template-name>
```

We can then go to the OpenShift UI and see the new application we created. This application has routes setup to service and run the flask application.

