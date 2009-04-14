
import urllib2
import json

class PyResource(object):
	_py_rest = None
	_resource_name = None

	def __init__(self, domain, resource_name):
		self._py_rest = PyRest(domain)
		self._resource_name = resource_name

	def __convert_rest_to_object(self, rest_object):
		# Get the name of the class
		key = rest_object.keys()[0]
		class_name = str(key.capitalize())

		# Generate the class code
		code = 'class ' + class_name + '(object):\n'

		code += '	def __init__(self):\n'
		for name, value in rest_object[key].iteritems():
			code += '		self._' + name + ' = None\n'
			code += '\n'

		for name, value in rest_object[key].iteritems():
			code += '	def set_' + name + '(self, value):\n'
			code += '		self._' + name + ' = value\n'
			code += '	def get_' + name + '(self):\n'
			code += '		return self._' + name + '\n'
			code += '	property(set_' + name + ', get_' + name + ')\n\n'

		# Add the class to a temp module
		code = compile(code, '<string>', 'exec')
		temp = imp.new_module("temp")
		sys.modules["temp"] = temp
		exec code in temp.__dict__

		# Create an instance of the object
		new_class = eval('temp.User')
		new_object = new_class()

		# Set all the properties with the values from the json
		for name, value in rest_object[key].iteritems():
			eval('new_object.set_' + name + '(value)')

		return new_object


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
		request = urllib2.Request(self._domain + path, get_params)
		request.get_method = lambda: 'GET'
		#request.add_header('Content-Type', 'your/contenttype')
		response = urllib2.urlopen(request)
		return json.loads(response.read())


