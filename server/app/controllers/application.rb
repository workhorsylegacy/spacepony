
require 'ezcrypto'


# Filters added to this controller apply to all controllers in the application.
# Likewise, all the methods added will be available for all controllers.

class ApplicationController < ActionController::Base
  helper :all # include all helpers, all the time

  # See ActionController::RequestForgeryProtection for details
  # Uncomment the :secret if you're not using the cookie session store
  protect_from_forgery # :secret => '550178a169990d8d7da2437dbe1ba0d6'
  
  # See ActionController::Base for details 
  # Uncomment this to filter the contents of submitted sensitive data parameters
  # from your application log (in this case, all fields with names like "password"). 
  # filter_parameter_logging :password

  before_filter :set_is_logged_in

  def set_is_logged_in
    @is_logged_in = is_logged_in?
  end

  protected

  def user_exists?(username)
    User.find_by_name(username) != nil
  end

  def valid_login?(username, password)
    user = User.find_by_name(username)

    # Return false if no user was found
    return false unless user

    # Return true if the name and password match a user
    hashed_password = User.encrypt_password(password, user.salt)
    user.hashed_password == hashed_password
  end

  def authenticate
    path = request.path.downcase

    # Use generic http authentication for json and xml
    if path.end_with?('.json') || path.end_with?('.xml')
      authenticate_http
    # Everything uses the custom html authentication
    else
      authenticate_html
    end
  end

  def authenticate_http
    return true if is_logged_in?

    authenticate_or_request_with_http_basic do |username, password|
      return log_in(username, password)
    end
  end

  def authenticate_html
    unless is_logged_in?
      redirect_to(:controller => :users, :action => :login)
      return false
    end

    return true
  end

  def log_in(username, password)
    result = valid_login?(username, password)
    return result unless result

    user =  User.find_by_name(username)
    session[:user_id] = user.id
    cookies[:user_id] = user.id.to_s
    cookies['user_name'] = user.name
    cookies['user_greeting'] = 'Howdy'
    result
  end

  def is_logged_in?
    session[:user_id] != nil
  end

  def was_request_from_this_site?(request)
    (request.env_table['HTTP_REFERER'] && 
    request.env_table['HTTP_REFERER'].index("http://" + request.env_table['HTTP_HOST']) == 0)
  end

  def get_originating_user_id
    raise "The 'get_originating_user_id' method needs to be overwritten in the controller, before calling the 'authorize_originating_user_only' method."
  end

  def is_originating_user_or_admin
    user = User.find_by_id(session[:user_id])

    return !(user == nil || (get_originating_user_id != user.id && user.user_type != 'A'))
  end

  def authorize_originating_user_only
    unless is_originating_user_or_admin
      flash[:notice] = "Only that user can access this page."
      respond_to do |format|
        format.html { head :unauthorized }
        format.json  { head :unauthorized }
        format.xml  { head :unauthorized }
      end
    end
  end
end
