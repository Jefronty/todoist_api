from . import os, quote, requests, sys, TodoistAPI, urljoin, urls
from .labels import Labels
from .projects import Projects
from .tasks import Tasks

class Todoist(TodoistAPI):
	"""combined access to todoist REST API"""
	
	__labels = None
	__projects = None
	__tasks = None

	urls = urls

	def __init__(self, token=None):
		if sys.version_info[0] > 2:
			super().__init__(token)
		else:
			# legacy code for Python2 usage
			super(Todoist, self).__init__(token)
		self.type = 'access'
		self.init_others()

	def init_others(self, token=None):
		_token = token or self.token
		if _token:
			self.labels = _token
			self.projects = _token
			self.tasks = _token

	@property
	def labels(self):
		if self.__labels is None and self.token:
			self.__labels = Labels(self.token)
		return self.__labels

	@labels.setter
	def labels(self, value):
		if isinstance(value, Labels):
			self.__labels = value
		elif isinstance(value, str):
			self.__labels = Labels(value)
		else:	
			self.__labels = Labels(self.token)

	@property
	def projects(self):
		if self.__projects is None and self.token:
			self.__projects = Projects(self.token)
		return self.__projects

	@projects.setter
	def projects(self, value):
		if isinstance(value, Projects):
			self.__projects = value
		elif isinstance(value, str):
			self.__projects = Projects(value)
		else:	
			self.__projects = Projects(self.token)

	@property
	def tasks(self):
		if self.__tasks is None and self.token:
			self.__tasks = Task(self.token)
		return self.__tasks

	@tasks.setter
	def tasks(self, value):
		if isinstance(value, Tasks):
			self.__tasks = value
		elif isinstance(value, str):
			self.__tasks = Tasks(value)
		else:	
			self.__tasks = Tasks(self.token)

	def user(self, token=None):
		"""get user info using provided token or instance token"""
		sess = self.token_check(token)
		if sess is False:
			return False
		resp = self.request(self.urls['user'], sess=sess)
		if resp and resp.status_code == 200:
			return resp.json()
		return False

	@staticmethod
	def user_info(token):
		"""get user info using provided token without requiring an instance"""
		if not token:
			return False
		resp = requests.get(urls['user'], headers={'Authorization': 'Bearer %s' % token})
		if resp and resp.status_code == 200:
			return resp.json()
		return False