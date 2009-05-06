
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
    authenticate_or_request_with_http_basic do |username, password|
      result = valid_login?(username, password)
      session[:user_id] = User.find_by_name(username).id if result

      result
    end
  end
end
