// Place your application-specific JavaScript functions and classes here
// This file is automatically included by javascript_include_tag :defaults

function get_cookie(name) {
	var value = null;
	document.cookie.split('; ').each(function(cookie) {
		var name_value = cookie.split('=');
		if(name_value[0] == name) {
			value = name_value[1];
		}
	});
	return value;
}

function set_cookie(name, value, expires) {
	var path = "/";
	var domain = null;
	var secure = null;

	var today = new Date();
	if(expires) {
		expires = expires * 1000 * 3600 * 24;
	}
	var value = name + '=' + escape(value) + 
					((expires) ? ';expires=' + new Date(today.getTime() + expires).toGMTString() : '') + 
					((path) ? ';path=' + path : '') + 
					((domain) ? ';domain=' + domain : '') + 
					((secure) ? ';secure' : '') + ';';
	document.cookie = value;
}

function delete_cookie(name) {
	if(get_cookie(name)) {
		set_cookie(name, get_cookie(name), -30);
	}
}

function is_logged_in() {
	var value = get_cookie('user_name');
	return (value != null && value != "");
}


