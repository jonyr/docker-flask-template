# Dockerizing a Flask application

A template project using docker and flask

## Getting started

Create a copy of .env.example and fill all the values and rename it as .env

## Installing and setting up Docker in Linux

1. Install docker: sudo apt install docker.io
2. Enable service: sudo systemctl enable docker
3. Add user permissons: sudo usermod -aG docker $USER
4. Activate changes to groups: newgrp docker
5. Reboot your computer
6. Verify all: docker run hello-world

## Running the project

1. Using VS Code Run and Debug option.
2. From VS Code terminal execute run_flask.sh script to start up the app using Flask Server
3. From VS Code terminal execute run_gunicorn.sh script to start up the app using Gunicorn

## Cli Commands

Using a terminal just run `flask` and cli commands will be listed.

1. `flask loc` This command counts how many lines of code are there. It only check files with the following extensions:
    - _.py_
    - _.html_
    - _.js_
    - _.css_
2. `flask token` generates a 32 length secret token.

## References

- [Setting up user permissions in Linux](https://docs.docker.com/engine/install/linux-postinstall/)
- [Developing inside a container](https://code.visualstudio.com/docs/remote/containers)
- [Debugging Flask app with Docker](https://waqqas.medium.com/debugging-flask-app-within-docker-12edf9321fd7)
- [docker-compose.yml](https://docs.docker.com/compose/compose-file/compose-file-v3/)


