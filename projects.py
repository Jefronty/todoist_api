from . import os, quote, sys, urljoin, urls
from .comments import Comments

class Projects(Comments):
	"""
	project and section management via the todoist REST API
	https://developer.todoist.com/api/v1/#tag/Projects
	subclass of Comments, inherits:
	add_comment: add a comment to a project
	comment: fetch a comment by ID
	comments: fetch comments by project ID
	delete_comment: delete a comment by ID
	update_comment: update a comment by ID
	"""
	url = urls['projects']
	sec_url = urls['sections']

	additional_fields = {
		'create': { # https://developer.todoist.com/api/v1/#tag/Projects/operation/create_project_api_v1_projects_post
			'color': 'color',
			'is_favorite': bool,
			'view_style': ('list', 'board')
		},
		'create_section': { # https://developer.todoist.com/api/v1/#tag/Sections/operation/create_section_api_v1_sections_post
			'order': int
		},
		'update': { # https://developer.todoist.com/api/v1/#tag/Projects/operation/update_project_api_v1_projects__project_id__post
			'name': str,
			'color': 'color',
			'is_favorite': bool,
			'view_style': ('list', 'board')
		}
	}

	def __init__(self, token=None):
		if sys.version_info[0] > 2:
			super().__init__(token)
		else:
			# legacy code for Python2 usage
			super(Projects, self).__init__(token)
		self.type = 'projects'

	def archive(self, id, token=None):
		"""
		use stored or provided token to archive a project
		Args:
			id (str): the ID of the project to archive
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
			r = self.request('%s/%s/archive' % (self.url, id), 'post', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def collaborators(self, id, token=None):
		"""
		use stored or provided token to fetch project collaborators
		Args:
			id (str): the ID of the project to archive
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			list: list of collaborators on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			r = self.request('%s/%s/collaborators' % (self.url, id), 'get', _sess)
			return r.json()
		except:
			return False

	def create(self, name, description=None, token=None, **kwargs):
		"""
		use stored or provided token to create a project
		Args:
			name (str): the name of the project to create
			description (str, optional): the description of the project
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the project, see self.additional_fields['create'] for allowed fields and types
		Returns:
			dict: the project data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'name': name}
			if description:
				payload['description'] = description
			# optional fields that may be included
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['create']):
					payload[key] = value
			r = self.request(self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def create_section(self, name, proj_id, token=None, **kwargs):
		"""
		use stored or provided token to create a section in a project
		Args:
			name (str): the name of the section to create
			proj_id (str): the ID of the project to create the section in
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the section, see self.additional_fields['create_section'] for allowed fields and types
		Returns:
			dict: the project data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'name': name, 'project_id': proj_id}
			# optional fields that may be included
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['create_section']):
					payload[key] = value
			r = self.request(self.sec_url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def delete(self, id, token=None):
		"""
		use stored or provided token to delete a project
		Args:
			id (str): the ID of the project to delete
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

	def delete_section(self, id, token=None):
		"""
		use stored or provided token to delete a section
		Args:
			id (str): the ID of the section to delete
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
			r = self.request('%s/%s' % (self.sec_url, id), 'delete', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def fetch(self, id=None, token=None):
		"""
		use stored or provided token to fetch project(s)
		Args:
			id (str, optional): the ID of the project to fetch
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			list | dict: a list of projects or single project dict on success
			None: if no token is set or invalid group type
			False: on error
		"""
		ret = []
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			if id:
				r = self.request('%s/%s' % (self.url, id), 'get', _sess)
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

	def project(self, id, token=None):
		"""alias for fetch method with id parameter to get a single project by ID"""
		return self.fetch(id, token)

	def sections(self, proj_id=None, token=None):
		"""
		use stored or provided token to fetch sections
		Args:
			proj_id (str, optional): the ID of the project to fetch sections for
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			list: a list of sections on success
			None: if no token is set or invalid group type
			False: on error
		"""
		ret = []
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			if proj_id:
				r = self.request('%s?project_id=%s' % (self.sec_url, proj_id), 'get', _sess)
				return r.json()
			r = self.request(self.sec_url, 'get', _sess)
			resp = r.json()
			ret += resp['results']
			while resp['next_cursor']:
				r = self.request('%s?cursor=%s' % (self.sec_url, resp['next_cursor']), 'get', _sess)
				resp = r.json()
				ret += resp['results']
			return ret
		except:
			return False

	def update(self, id, token=None, **kwargs):
		"""
		use stored or provided token to update a project
		Args:
			id (str): the ID of the project to update
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the project, see self.additional_fields['update'] for allowed fields and types
		Returns:
			dict: the project data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {}
			# optional fields that may be included
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['update']):
					payload[key] = value
			if not payload:
				return False
			r = self.request('%s/%s' % (self.url, id), 'post', _sess, payload)
			return r.json()
		except:
			return False

	def update_section(self, id, name, token=None):
		"""
		use stored or provided token to update a section
		Args:
			id (str): the ID of the section to update
			name (str): the new name of the section
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			dict: the section data on success
			None: if no token is set
			False: on error
		"""
		if not name.strip():
			return False
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'name': name}
			r = self.request('%s/%s' % (self.sec_url, id), 'post', _sess, payload)
			return r.json()
		except:
			return False

	def unarchive(self, id, token=None):
		"""
		use stored or provided token to unarchive a project
		Args:
			id (str): the ID of the project to unarchive
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
			r = self.request('%s/%s/unarchive' % (self.url, id), 'post', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False