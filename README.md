# Flask-text-similarity-api using Flask, Docker, Docker-Compose and MongoDB
*NOTE: This is NOT a production grade script, so please do not utilize for projects that contain sensitive information.*

This is a simple demonstration of a backend ReST API using flask, docker and docker-compose demonstrating a simple API
for comparing two pieces of text. This API also utilizes mongoDB in order to keep track of users, store hashed passwords, as well as demonstrate a primitive currency per usage utiiizing tokens.This project was created in an Ubuntu environment, so the instructions will be shown as linux commands

## How to use:
1. Download the docker-compose.yml file, as well as the two folders, db and web, both of which contain Dockerfiles for building the API. the web directory contains the main python app script, as well as the requirements.txt file for the script.

2. Run by building the docker-compose file: 
    > sudo docker-compose build

3. then starting up the docker instance:
    > sudo docker-compose up

4. Once the instance is running locally, send the API requests to your localhost, at the appropriate  endpoint using an API development tool such as Postman. 
