tags_metadata = [
    {
        "name": "home",
        "description": "Home displays all current tasks"
    },
    {   "name": "get_item",
        "description": "Retrieve an item by ID"
    },
    {   "name": "post_item",
        "description": "Creates a new task & inserts to DB"
    },
    {   "name": "update_item",
        "description": "Updates an item by ID"
    },
    {   "name": "delete_item",
        "description": "Deletes item by ID"
    },
]

app_description = """ 
A simple ToDo app using fast API and SqlAlchemy

## Users can
* Retrieve all tasks
* Search for tasks via query
* Limit number of results returned
* Retrieve a single task
* Create a task
* Update a task
* Delete a task

* Sorting
    * Enum stores all sort types so user can sort by
        * Task name ascending or descending
        * Task importance ascending or descending

## To be implemented

* User can mark a task complete


"""