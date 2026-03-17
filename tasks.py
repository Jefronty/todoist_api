from . import os, quote, re, sys, urljoin, urls
from .comments import Comments

class Tasks(Comments):
	"""
	task management via the todoist REST API
	https://developer.todoist.com/api/v1/#tag/Tasks
	subclass of Comments, inherits:
	add_comment: add a comment to a task
	comment: fetch a comment by ID
	comments: fetch comments by task ID
	delete_comment: delete a comment by ID
	update_comment: update a comment by ID
	"""
	url = urls['tasks']

	additional_fields = {
		'create': { # https://developer.todoist.com/api/v1/#tag/Tasks/operation/create_task_api_v1_tasks_post
			'description': str,
			'project_id': 'ID',
			'section_id': 'ID',
			'parent_id': 'ID',
			'order': int,
			'labels': list,
			'priority': (1, 2, 3, 4),
			'due_string': str,
			'due_date': 'date',
			'due_datetime': str,
			'due_lang': str,
			'assignee_id': int,
			'duration': int,
			'duration_unit': ('minute', 'day'),
			'deadline_date': 'date'
		},
		'fetch': { # https://developer.todoist.com/api/v1/#tag/Tasks/operation/get_tasks_api_v1_tasks_get
			'project_id': 'ID',
			'section_id': 'ID',
			'parent_id': 'ID',
			'label': str,
			'filter': str,
			'lang': str,
			'ids': list
		},
		'quick': { # https://developer.todoist.com/api/v1/#tag/Tasks/operation/quick_add_api_v1_tasks_quick_post
			'note': str,
			'reminder': str, # date or datetime string
			'auto_reminder': bool,
			'meta': bool
		}
	}

	group_pattern = re.compile(r'^(project|section|task|parent)s?$', re.IGNORECASE)

	def __init__(self, token=None):
		if sys.version_info[0] > 2:
			super().__init__(token)
		else:
			# legacy code for Python2 usage
			super(Tasks, self).__init__(token)
		self.type = 'tasks'

	def close(self, id, token=None):
		"""
		use stored or provided token to close a task
		Args:
			id (str): the ID of the task to close
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			True: on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			r = self.request('%s/%s/close' % (self.url, id), 'post', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def create(self, content, due_date=None, token=None, **kwargs):
		"""
		use stored or provided token to create a task
		Args:
			content (str): the content of the task to create
			due_date (str, optional): the due date for the task
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the task, see self.additional_fields['create'] for allowed fields and types
		Returns:
			dict: the task data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'content': content}
			# optional fields that may be included
			if due_date and self.validate_param('due_date', due_date, self.additional_fields['create']['due_date']):
				payload['due_date'] = due_date
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['create']):
					payload[key] = value
			r = self.request(self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def delete(self, id, token=None):
		"""
		use stored or provided token to delete a task
		Args:
			id (str): the ID of the task to delete
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			True: on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			r = self.request('%s/%s' % (self.url, id), 'delete', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def fetch(self, id=None, token=None, **kwargs):
		"""
		use stored or provided token to fetch tassks or a task by ID
		Args:
			id (str, optional): the ID of the task to fetch
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the request, see self.additional_fields['fetch'] for allowed fields and types
		Returns:
			list: a list of tasks on success
			None: if no token is set or invalid group type
			False: on error
		"""
		ret = []
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			params = []
			task_id = id or kwargs.get('task_id', None)
			if task_id:
				r = self.request('%s/%s' % (self.url, id), 'get', _sess)
				return r.json()
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['fetch']):
					if key == 'ids' and isinstance(value, list):
						value = ','.join([str(i) for i in value])
					params.append('%s=%s' % (key, quote(str(value))))
			if params:
				r = self.request('%s?%s' % (self.url, '&'.join(params)), 'get', _sess)
			else:
				r = self.request(self.url, 'get', _sess)
			base_url = r.url
			resp = r.json()
			if 'results' in resp:
				ret += resp['results']
			while resp.get('next_cursor', None):
				r = self.request('%s&cursor=%s' % (base_url, resp['next_cursor']), 'get', _sess)
				resp = r.json()
				if resp.get('results', None):
					ret += resp['results']
			return ret
		except:
			return False

	def move(self, id, group, group_id, token=None):
		"""
		use stored or provided token to move a task to project or section
		Args:
			id (str): the ID of the task to move
			group (str): the type of group to fetch comments for, either 'project' or 'section' or parent 'task'
			group_id (str): the ID of the project, section, or parent task to move the task to
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			dict: the task data on success
			None: if no token is set or invalid group type
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			gtype = self.group_type(group)
			if gtype == 'project':
				id_key = 'project_id'
			elif gtype == 'section':
				id_key = 'section_id'
			elif gtype in ('task', 'parent'):
				id_key = 'parent_id'
			else:
				return None
			payload = {id_key: group_id}
			r = self.request('%s/%s/move' % (self.url, id), 'post', _sess, payload)
			return r.json()
		except:
			return False

	def quick_add(self, content, token=None, **kwargs):
		"""
		use stored or provided token to create a task using the quick add syntax
		content can contain #projectname, /sectionname, @labelname, prioroity (p1, p2, ...), {duedate}, //description
		Args:
			content (str): the content of the task to create, using the quick add syntax
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the task, see self.additional_fields['quick'] for allowed fields and types
		Returns:
			dict: the task data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'text': content}
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['quick']):
					payload[key] = value
			r = self.request('%s/quick' % self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def reopen(self, id, token=None):
		"""
		use stored or provided token to reopen a task
		Args:
			id (str): the ID of the task to reopen
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			True: on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			r = self.request('%s/%s/reopen' % (self.url, id), 'post', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def task(self, id, token=None):
		"""alias for fetch method with id parameter to get a single task by ID"""
		return self.fetch(id, token)

	def update(self, id, token=None, **kwargs):
		"""
		use stored or provided token to update a task
		Args:
			id (str): the ID of the task to update
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the task, see self.additional_fields['update'] for allowed fields and types
		Returns:
			dict: the task data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {}
			# optional fields that may be included
			params = self.additional_fields['create'].copy()
			params['content'] = str
			for key, value in kwargs.items():
				if self.validate_param(key, value, params):
					payload[key] = value
			if not payload:
				return False
			r = self.request('%s/%s' % (self.url, id), 'post', _sess, payload)
			return r.json()
		except:
			return False