
import urllib2, urllib
import json
import re, imp, sys, inspect

class PyResourceClass(object):
	_py_rest = None
	_resource_name = None

	def save(self):
		# Get the class
		klass = type(self)
		json_object = { klass._resource_name : self.__dict__ }

		# Save a new model
		if not self.__dict__.has_key('id'):
			path = klass._resource_name + 's'
			klass._py_rest.post(path, json_object)

		# Update an existing model
		else:
			path = klass._resource_name + 's/' + str(self.__dict__['id'])
			klass._py_rest.put(path, self.__dict__)

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
		new_object = eval(class_name + '()')
		for name, value in json_object[key].iteritems():
			new_object.__dict__[name] = value

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

		# Return the class
		new_class = eval('temp.' + class_name)
		globals()[class_name] = new_class
		return globals()[class_name]

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

	# FIXME: Update this to get the cookies too?
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
		request.add_header("Content-Type", "application/json")

		# FIXME: Change this to only return the http status code and response
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError:
			raise RestError("Could not connect to: " + self._domain + path)
		return json.loads(response.read())

	def post(self, path, json_object = {}):
		# Send the request and get the response
		response = None
		request = urllib2.Request(self._domain + path)
		request.get_method = lambda: 'POST'
		request.add_header("Content-Type", "application/json")
		request.add_data(str(json_object))

		# FIXME: Change this to only return the http status code and response
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError, err:
			if err.code == 422: # Unprocessed Entity
				server_errors = json.loads(err.read())
				errors = ""
				for field, error in server_errors:
					errors += field + ' ' + error + '\n'
				raise RestError(errors)
			elif err.code == 500: # Internal Server Error
				print err.read()
				raise RestError("Error on the server")
				return None
			else:
				#print err.read()
				return None
				raise RestError("Could not connect to: " + self._domain + path)
		return json.loads(response.read())


