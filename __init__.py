import os, sys, re
import requests
if sys.version_info[0] > 2:
	from urllib.parse import quote, urljoin
else:
	from urllib import quote
	from urlparse import urljoin

__all__ = ['TodoistAPI', 'labels', 'projects', 'tasks', 'todoist']

urls = {
	'comments': 'https://api.todoist.com/api/v1/comments',
	'labels': 'https://api.todoist.com/api/v1/labels',
	'projects': 'https://api.todoist.com/api/v1/projects',
	'sections': 'https://api.todoist.com/api/v1/sections',
	'tasks': 'https://api.todoist.com/api/v1/tasks',
	'user': 'https://api.todoist.com/api/v1/user'
}

class TodoistAPI(object):
	"""
	parent class to interact with todoist
	resources:
		https://developer.todoist.com/rest/v2
		https://developer.todoist.com/api/v1/
	"""

	id_pattern = re.compile(r'^\w+$')
	date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

	color_map = { # https://developer.todoist.com/guides/#colors
		'berry_red': {'id': 30, 'css': '#B8255F'},
		'red': {'id': 31, 'css': '#DC4C3E'},
		'orange': {'id': 32, 'css': '#C77100'},
		'yellow': {'id': 33, 'css': '#B29104'},
		'olive_green': {'id': 34, 'css': '#949C31'},
		'lime_green': {'id': 35, 'css': '#7ECC49'},
		'green': {'id': 36, 'css': '#369307'},
		'mint_green': {'id': 37, 'css': '#42A393'},
		'teal': {'id': 38, 'css': '#148FAD'},
		'sky_blue': {'id': 39, 'css': '#319DC0'},
		'light_blue': {'id': 40, 'css': '#6988A4'},
		'blue': {'id': 41, 'css': '#4180FF'},
		'grape': {'id': 42, 'css': '#692EC2'},
		'violet': {'id': 43, 'css': '#CA3FEE'},
		'lavender': {'id': 44, 'css': '#A4698C'},
		'magenta': {'id': 45, 'css': '#E05095'},
		'salmon': {'id': 46, 'css': '#C9766F'},
		'charcoal': {'id': 47, 'css': '#808080'},
		'grey': {'id': 48, 'css': '#999999'},
		'taupe': {'id': 49, 'css': '#8F7A69'}
	}

	try:
		rePatternType = re.Pattern
	except:
		rePatternType = type(re.compile(r''))

	def __init__(self, token=None):
		self.token = token

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, str(self.token or None))

	def __str__(self):
		return self.__class__.__name__

	@property
	def live(self):
		return self.__live

	def request(self, url, method='get', sess=None, data=None):
		"""
		execute requests method using given seeion or insnstance session
		return False on error
		"""
		try:
			_sess = sess or self.sess
			if not data:
				return getattr(_sess, method.lower())(url)
			return getattr(_sess, method.lower())(url, json=data)
		except:
			return False

	@property
	def token(self):
		return self._token

	@token.setter
	def token(self, token=None):
		self._token = str(token or '')
		if self._token:
			self.__live = True
			self.sess = requests.session()
			self.sess.headers.update({'Authorization': 'Bearer %s' % token})
		else:
			self.__live = False
			self.sess = None

	def token_check(self, token):
		"""check whether instance has a set token and check provided token value"""
		if not self.live and not token:
			return False
		if token and not self.live:
			# set session token to provided token
			self.token = token
			return None
		elif self.live and token:
			# use provided token, but keep previously set token value for future
			_sess = requests.session()
			_sess.headers.update({'Authorization': 'Bearer %s' % token})
			return _sess
		return None

	def validate_param(self, param, val, allowed):
		"""
		validate that param is allowed and has an acceptable value
		return True if valid, False if not
		"""
		if param in allowed:
			if allowed[param] == 'ID':
				return self.id_pattern.match(val)
			elif allowed[param] == 'color':
				if val in self.color_map:
					return True
				elif isinstance(val, int) and 30 <= val <= 49:
					for name, info in self.color_map.items():
						if info['id'] == val:
							break
					print('use color name %s instead of ID %d' % (name, val))
					return False
				elif isinstance(val, str) and val.isdigit() and 30 <= int(val) <= 49:
					for name, info in self.color_map.items():
						if str(info['id']) == val:
							break
					print('use color name %s instead of ID %s' % (name, val))
					return False
				return False
			elif param == 'date':
				return self.date_pattern.match(val)
			elif isinstance(allowed[param], type) and isinstance(val, allowed[param]):
				return True
			elif isinstance(allowed[param], (list, tuple)) and val in allowed[param]:
				return True
			elif isinstance(allowed[param], (function, instancemethod, builtin_function_or_method)):
				return allowed[param](val)
			elif isinstance(allowed[param], rePatternType):
				return bool(allowed[param].match(val))
		return False