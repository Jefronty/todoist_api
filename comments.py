from . import os, quote, sys, TodoistAPI, urljoin, urls

class Comments(TodoistAPI):
	"""
	comment management via the todoist REST API
	https://developer.todoist.com/api/v1/#tag/Comments
	Intended to be used as a parent class for Projects and Tasks
	"""
	url = urls['comments']

	comment_fields = {
		'add_comment': { # https://developer.todoist.com/api/v1/#tag/Comments/operation/create_comment_api_v1_comments_post
			'attachment': dict
			#
			#'resource_type': str ['file',]
			#'file_name': str,
			#'file_url': str,
			#'file_type': str [mime type],
			#
		}
	}

	def __init__(self, token=None):
		if sys.version_info[0] > 2:
			super().__init__(token)
		else:
			# legacy code for Python2 usage
			super(Comments, self).__init__(token)
		self.type = 'comments'

	def add_comment(self, content, group_id, token=None, **kwargs):
		"""
		use stored or provided token to add a comment to a task or project
		Args:
			content (str): the content of the comment to add
			group_id (str): the ID of the project or task to add the comment to
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the comment, see self.comment_fields['add_comment'] for allowed fields and types
		Returns:
			dict: the comment data on success
			None: if no token is set or invalid group type
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'content': content}
			if self.__class__.__name__ == 'Projects':
				payload['project_id'] = group_id
			elif self.__class__.__name__ == 'Tasks':
				payload['task_id'] = group_id
			else:
				return False
			# optional fields that may be included
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.comment_fields['add_comment']):
					payload[key] = value
			r = self.request(self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def comment(self, id, token=None):
		"""
		use stored or provided token to fetch a comment by ID
		Args:
			id (str): the ID of the comment to fetch
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			dict: the comment data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			r = self.request('%s/%s' % (self.url, id), 'get', _sess)
			return r.json()
		except:
			return False

	def comments(self, group_id, token=None):
		"""
		use stored or provided token to fetch comments for a task or project
		Args:
			group_id (str): the ID of the project or task to fetch comments for
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			list: a list of comments on success
			None: if no token is set or invalid group type
			False: on error
		"""
		ret = []
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			if self.__class__.__name__ == 'Projects':
				id_key = 'project_id'
			elif self.__class__.__name__ == 'Tasks':
				id_key = 'task_id'
			else:
				return ret
			r = self.request('%s?%s=%s' % (self.url, id_key, quote(str(group_id))), 'get', _sess)
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

	def delete_comment(self, id, token=None):
		"""
		use stored or provided token to delete a comment
		Args:
			id (str): the ID of the comment to delete
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
			if self.__class__.__name__ not in ('Projects', 'Tasks'):
				return ret
			r = self.request('%s/%s' % (self.url, id), 'delete', _sess)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def update_comment(self, id, content, token=None):
		"""
		use stored or provided token to update a comment
		Args:
			id (str): the ID of the comment to update
			content (str): the new content for the comment
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			dict: the comment data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'content': content}
			r = self.request('%s/%s' % (self.url, id), 'post', _sess, payload)
			return r.json()
		except:
			return False