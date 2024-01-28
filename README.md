# Social Media API

Social Media API - is a project aimed at developing and providing an API for a social network. This API can be used for creating, reading, updating, and deleting user data, posts, comments, likes, and supports scheduled post publication.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation Git](#installation)
- [Run with Docker](#run-with-docker)

## Introduction

Created using Django REST API as a test task.

### Features:
- Email-Based Authentication
- API documentation
- CRUD operations for Profile, Post, Comment, Like,
- Add images for Profile and Post
- Scheduling posts for publication (Celery)

## Installation

1. Clone the repository:

   ```
   https://github.com/bezhevets/social_media_api.git
   ```
2. Copy .env_sample -> env. and populate with all required data:
   ```
   POSTGRES_HOST= your db host
   POSTGRES_DB= name of your db
   POSTGRES_USER= username of your db user
   POSTGRES_PASSWORD= your db password
   SECRET_key=" your django secret key "
   ```
3. Create a virtual environment (OR LOOK WITH DOCKER):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:

   - On macOS and Linux:
   ```source venv/bin/activate```
   - On Windows:
   ```venv\Scripts\activate```
5. Install project dependencie:
   ```
    pip install -r requirements.txt
   ```
6. Run database migrations:
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```
7. Run Celeri:
   ```
   celery -A app worker --loglevel=INFO --pool=solo
   ```
### Or take the first 3 steps and run with Docker
   Docker must be already installed
   ```
   docker-compose up --build
   ```
   
   
## Run with Docker
Docker should be installed.

1. Pull docker container:

   ```
   docker push ke1erman/social_media_api
   ```
2. Run docker container
   ```
    docker-compose build
    docker-compose up
   ```


