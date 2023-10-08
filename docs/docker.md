# Why Docker
Docker lets us define a runtime explicitly for the application, detaching the system of the user from the application itself.

# Docker image of the app
To first create a docker image, you have to run:
```console
sudo docker buildx build . -t canvas
```
or

```console
sudo docker build . -t canvas
```
depending on your system. 

# Running the docker image
To run the created image, use 
```console
sudo docker run -d -p 5000:5000 canvas
```
To run canvas as (-d) detached from the terminal process and (-p) connecting port 5000 to 5000 

Now the application should be available at localhost:5000

# Docker-compose
These commands can be combined and predefined with a single
```console
sudo docker-compose up
```
command, which takes the arguments from compose.yml, which defines the ports and settings in a yml format.