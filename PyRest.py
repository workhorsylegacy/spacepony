

# This library is obsolete. Use pyactiveresource instead.

"""
import urllib2, urllib
import json
import re, imp, sys, inspect

class Response(object):
	def __init__(self, code, body):
		self._code = code
		self._body = body

	@property
	def code(self):
		return self._code

	@code.setter
	def code(self, value):
		self._code = value

	@property
	def body(self):
		return self._body

	@body.setter
	def body(self, value):
		self._body = value

class PyResourceClass(object):
	_py_rest = None
	_resource_name = None

	def save(self):
		# Get the class
		klass = type(self)
		json_object = { klass._resource_name : self.__dict__ }
		response = None

		# Save a new model
		if not self.__dict__.has_key('id'):
			path = klass._resource_name + 's.json'
			response = klass._py_rest.post(path, json_object)
		# Update an existing model
		else:
			path = klass._resource_name + 's/' + str(self.id) + '.json'
			response = klass._py_rest.put(path, json_object)

		# Deal with the response code
		if response.code == 201: # Created
			self.id = response.body[klass._resource_name]['id']
		elif response.code == 200: # OK
			pass
		elif response.code == 422: # Unprocessed Entity
			server_errors = response.body
			errors = ""
			for field, error in server_errors:
				errors += field + ' ' + error + '\n'
			raise RestError(errors)
		elif response.code == 500: # Internal Server Error
			print response.read()
			raise RestError("Error on the server")
			return None
		else:
			raise Exception('Unknown error when saving: ' + str(response.code) + ' ' + str(response.body))

	def delete(self):
		# Get the class
		klass = type(self)
		response = None

		# Delete the model
		path = klass._resource_name + 's/' + str(self.id) + '.json'
		response = klass._py_rest.delete(path)

		# Deal with the response code
		if response.code == 200: # OK
			self.__dict__.pop('id')
		else:
			raise Exception('Unknown error when deleting: ' + str(response.code) + ' ' + str(response.body))

	@classmethod
	def find_all(klass):
		response = klass._py_rest.get(klass._resource_name + 's.json')

		retval = []
		for json_object in response.body:
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

		# Get the response
		response = None
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError, err:
			response = err

		# Return the status code and response
		body = response.read()
		if body == ' ' or body == '':
			return Response(response.code, body)
		else:
			return Response(response.code, json.loads(body))

	def post(self, path, json_object = {}):
		# Send the request and get the response
		response = None
		request = urllib2.Request(self._domain + path)
		request.get_method = lambda: 'POST'
		request.add_header("Content-Type", "application/json")
		request.add_data(str(json_object))

		# Get the response
		response = None
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError, err:
			response = err

		# Return the status code and response
		body = response.read()
		if body == ' ' or body == '':
			return Response(response.code, body)
		else:
			return Response(response.code, json.loads(body))

	def put(self, path, json_object = {}):
		# Send the request and get the response
		response = None
		request = urllib2.Request(self._domain + path)
		request.get_method = lambda: 'PUT'
		request.add_header("Content-Type", "application/json")
		request.add_data(str(json_object))

		# Get the response
		response = None
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError, err:
			response = err

		# Return the status code and response
		body = response.read()
		if body == ' ' or body == '':
			return Response(response.code, body)
		else:
			return Response(response.code, json.loads(body))

	def delete(self, path):
		# Send the request and get the response
		response = None
		request = urllib2.Request(self._domain + path)
		request.get_method = lambda: 'DELETE'
		request.add_header("Content-Type", "application/json")

		# Get the response
		response = None
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError, err:
			response = err

		# Return the status code and response
		body = response.read()
		if body == ' ' or body == '':
			return Response(response.code, body)
		else:
			return Response(response.code, json.loads(body))
"""

