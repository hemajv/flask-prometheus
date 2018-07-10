# flask-prometheus
Flask application setup with Prometheus to export metrics

## Deploying the application and running locally on your system
### Building the docker image
```
      docker build . -t flask-prom
```
### Running the container 
```
      docker run -p 5000:5000 flask-prom
```

# Running the application on OpenShift
app.yaml is the template file (save it locally on your system) from which we can deploy our flask application (app.py) and have it running on OpenShift. 
## Login to OpenShift and enter your credentials
```
      oc login
```
Save the app.yaml template file locally on your system
## We now create the template for OpenShift to use as follows
```
      oc create -f app.yaml
```
## We then create a new application using this template
```
      oc new-app <template-name>
```

We can then go to the OpenShift UI and see the new application we created. This application has routes setup to service and view the Prometheus metrics.

## Navigate to view metrics
To view the metrics, we open the browser and navigate to the URL created for your application.
```
      https://<Your application route URL>/metrics
```
This is where all the Prometheus metrics are being populated.

You can specify your own routes in the flask application and navigate to the pages in the browser accordingly to view the contents. 
