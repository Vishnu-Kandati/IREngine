import requests

class AbstractHandler(object): 

	"""Parent class of all concrete handlers"""

	def __init__(self, _nxt): 

		"""change or increase the local variable using nxt"""

		self._nxt = nxt 

	def handle(self, url): 

		"""It calls the processRequest through given request"""

		handled = self.processRequest(request) 

		"""case when it is not handled"""

		if not handled: 
			self._nxt.handle(url) 

	def processRequest(self, request): 

		"""throws a NotImplementedError"""

		raise NotImplementedError('First implement it !') 


class StatusCodeHandler(AbstractHandler): 

	"""Concrete Handler # 1: Child class of AbstractHandler"""

	def processRequest(self, request): 

		'''return True if request is handled '''
        r = requests.get(url)
        if r.status_code == 200:
            return True
		


class RobotscheckHandler(AbstractHandler): 

	"""Concrete Handler # 2: Child class of AbstractHandler"""

	def processRequest(self, request): 

		'''return True if the request is handled'''

		rp = urllib.robotparser.RobotFileParser()
        rp.set_url(domain + '/robots.txt')
        rp.read()
        if not rp.can_fetch('*', url):  # robots.txt mentions that the link should not be parsed
            print('robots.txt does not allow to crawl', url)
            errors.append('Robots Exclusion')
            return False
        else:
            return True

class MimeHandler(AbstractHandler): 

	"""Concrete Handler # 3: Child class of AbstractHandler"""

	def processRequest(self, request): 

		if 'text/html' in r.headers['Content-Type']:
            return True
        else:  
            errors.append('Invalid MIME type')
            return False