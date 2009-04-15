
import urllib2
import json
import re, imp, sys, inspect

class PyResourceModel(object):
	def __init__(self):
		self._properties = {}

	def __getattr__(self, name):
		p = self._properties

		if p.has_key(name):
			return p[name]
		else:
			return None

class PyResourceClass(object):
	_py_rest = None
	_resource_name = None

	@classmethod
	def find_all(klass):
		json_objects = klass._py_rest.get(klass._resource_name + 's.json')

		retval = []
		for json_object in json_objects:
			retval.append(klass.__json_to_object(json_object))

		return retval

	@classmethod
	def __json_to_object(klass, json_object):
		# Get the name of the class
		key = json_object.keys()[0]
		class_name = str(key.capitalize())

		# Set all the properties with the values from the json
		for name, value in json_object[key].iteritems():
			eval('new_object.set_' + name + '(value)')

		return new_object

class PyResource(object):
	@classmethod
	def connect(klass, domain, resource_name):
		# Get the name of the class
		class_name = str(resource_name.capitalize())

		# Generate the class code
		code = 'import PyRest\n'
		code += 'class ' + class_name + '(PyRest.PyResourceClass):\n'
		code += '	_py_rest = PyRest.PyRest(\"' + domain + '\")\n'
		code += '	_resource_name = \"' + resource_name + '\"\n\n'

		# Add the class to a temp module
		code = compile(code, '<string>', 'exec')
		temp = imp.new_module("temp")
		sys.modules["temp"] = temp
		exec code in temp.__dict__

		# Create an instance of the object
		return eval('temp.' + class_name)

class RestError(Exception):
	pass

class PyRest(object):
	_cookies = []
	_domain = None

	def __init__(self, domain):
		# Save the domain, and ensure it has a ending forward slash
		self._domain = domain
		if not self._domain.endswith('/'):
			self._domain +=  '/'

	# FIXME: Update this to get the cookies too
	def get(self, path, params = {}):
		# Assemble to http get arguments in url format
		get_params = ''
		if len(params) > 0:
			get_params += '?'
			for key, value in params:
				get_params += key + '=' + urllib.urlencode(value) + ';'

		# Send the request and get the response
		response = None
		request = urllib2.Request(self._domain + path, get_params)
		request.get_method = lambda: 'GET'
		#request.add_header('Content-Type', 'your/contenttype')
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError:
			raise RestError("Could not connect to: " + self._domain + path)
		return json.loads(response.read())


