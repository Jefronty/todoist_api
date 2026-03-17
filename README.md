Inspired by the API documentation at https://developer.todoist.com/api/v1/

# Class structure


```
+-- TodoistAPI (__init__.py)
|    +-- Comments (comments.py)
|        +-- Projects (projects.py)
|        +-- Tasks (task.py)
|    +-- Labels (labels.py)
|    +-- Todoist (todoist.py)
```

## Example usage

```
from todoist_api.todoist import Todoist

# from Settings > Integrations > Developer on todoist.com
api_token = 'my_unique_token'

td = Todoist(api_token)

tasks = td.tasks.fetch()

# delete first task
if not td.tasks.delete(tasks[0]['id']):
	print('failed to delete %s' % tasks[0]['content'])

my_info = td.user()
```

The base class is named TodoistAPI, it has child classes Comments, Labels, and Todoist.  Comments has Projects and Tasks as child classes.
The Todoist class has all other descendants of TodoistAPI as properties and can be used to manage any aspect of a Todoist account.
Each class instance will store the API token as a property, but methods can take a token value as a parameter to access another Todoist account.
Projects class manages both projects and sections