from . import os, quote, sys, TodoistAPI, urljoin, urls

class Labels(TodoistAPI):
	"""
	label management via the todoist REST API
	https://developer.todoist.com/api/v1/#tag/Labels
	"""
	url = urls['labels']

	additional_fields = {
		'create': { # https://developer.todoist.com/api/v1/#tag/Labels/operation/create_label_api_v1_labels_post
			'order': int,
			'color': 'color',
			'is_favorite': bool
		},
		'update': { # https://developer.todoist.com/api/v1/#tag/Labels/operation/update_label_api_v1_labels__label_id__post
			'name': str,
			'order': int,
			'color': 'color',
			'is_favorite': bool
		}
	}

	def __init__(self, token=None):
		if sys.version_info[0] > 2:
			super().__init__(token)
		else:
			# legacy code for Python2 usage
			super(Labels, self).__init__(token)
		self.type = 'Labels'

	def create(self, name, token=None, **kwargs):
		"""
		use stored or provided token to create a label
		Args:
			name (str): the name of the label to create
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the label, see self.label_fields['create'] for allowed fields and types
		Returns:
			dict: the label data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'name': name}
			# optional fields that may be included
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['create']):
					payload[key] = value
			r = self.request(self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False

	def delete(self, id, token=None):
		"""
		use stored or provided token to delete a label
		Args:
			id (str): the ID of the label to delete
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

	def fetch(self, id=None, token=None, omit_personal=False):
		"""
		use stored or provided token to fetch labels or a label by ID
		Args:
			id (str, optional): the ID of the label to fetch
			token (str, optional): a token to use for this request, if not set will use instance token
			omit_person (bool): option to exclude personal labels
		Returns:
			dict: the label data on success
			None: if no token is set
			False: on error
		"""
		ret = []
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			if id:
				if id == 'shared' and omit_personal:
					r = self.request('%s/%s?omit_personal=True' % (self.url, id), 'get', _sess)
				else:
					r = self.request('%s/%s' % (self.url, id), 'get', _sess)
				if id != 'shared':
					return r.json()
			else:
				r = self.request(self.url, 'get', _sess)
			base_url = r.url
			if '?' in base_url:
				glue = '&'
			else:
				glue = '?'
			resp = r.json()
			if 'results' in resp:
				ret += resp['results']
			while resp.get('next_cursor', None):
				r = self.request('%s%scursor=%s' % (base_url, glue, resp['next_cursor']), 'get', _sess)
				resp = r.json()
				if resp.get('results', None):
					ret += resp['results']
			return ret
		except:
			return False

	def label(self, id, token=None):
		"""alias for fetch method with id parameter to get a single label by ID"""
		return self.fetch(id, token)

	def rename(self, name, new_name, token=None):
		"""
		use stored or provided token to rename a shared label
		Args:
			name (str): the existing name of the label
			new_name(str): the new name to give the label
			token (str, optional): a token to use for this request, if not set will use instance token
		Returns:
			dict: the label data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			payload = {'name': name, 'new_name': new_name}
			r = self.request('%s/shared/rename' % self.url, 'post', _sess, payload)
			if not r.content:
				return True
			return r.json()
		except:
			return False

	def update(self, id, token=None, **kwargs):
		"""
		use stored or provided token to update a label
		Args:
			id (str): the ID of the label to update
			token (str, optional): a token to use for this request, if not set will use instance token
			**kwargs: optional fields to include in the label, see self.additional_fields['update'] for allowed fields and types
		Returns:
			dict: the label data on success
			None: if no token is set
			False: on error
		"""
		_sess = self.token_check(token)
		if _sess is False:
			return None
		try:
			url = '%s/%s' % (self.url, id)
			payload = {}
			# optional fields that may be included
			fields = self.additional_fields['create'].copy()
			fields['name'] = str
			for key, value in kwargs.items():
				if self.validate_param(key, value, self.additional_fields['update']):
					payload[key] = value
			if not payload:
				return False
			r = self.request(self.url, 'post', _sess, payload)
			return r.json()
		except:
			return False