# Deploying to the Cloud

The dockerized version of the application can be deployed to a Cloud VM for deployment. 

It is recommended to use a VM with some computing resources to spare, as some of the filters require substantial processing.

For a Smart Canvas student project, https://docs.csc.fi/cloud/pouta/ is a good option that provides free computing resources. 

As of May 2025, the dockerized version of the application should work "out of the box" both locally and when cloned to a cloud environment, with the Flask server running on port 5000 and React frontend on port 5173.

Refer to the instructions of your cloud service of choice. 

# Camera not showing when deployed to the cloud?

In order to access web camera, modern browsers require secure https:// connection. 

One handy way to obtain a certificate without much hassle is to use a Caddy. Refer to https://caddyserver.com/docs/automatic-https for more information.