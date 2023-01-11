# FastAPI-ToDo-List

[LiveLink to API](http://167.99.219.161:8050/docs)

A simple ToDo app using fast API and SqlAlchemy as a learning exercise.

- Users can
- Filter tasks by query
- Retrieve all tasks
- Retrieve a single task by id
- Create a task
- Update a task by id
- Delete a task by id

- Sorting
    - Enum stores all sort types so user can sort by
        - Task name ascending or descending
        - Task importance ascending or descending

## Documentation

Access API documentation with /docs when using the API to see full functionality

## Future development

* Limit main todo list to read only for unauthorised users

* Create users that have a random password so they can access their own todo list

* Limit amount of hits per IP to limit abuse of the API

## Tests

Unit test created with pytest, run in console with `python -m pytest` add `-rP` for extra summary info


## To Run locally

uvicorn main:app --reload --port 8000

## To Run in Docker

* Install docker
* Run `docker-compose build`
* Run `docker-compose up`
* Access through port 8050