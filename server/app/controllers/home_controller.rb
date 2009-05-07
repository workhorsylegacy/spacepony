class HomeController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []

  def index
    respond_to do |format|
      format.html # index.html.erb
      format.json  { render :json => nil }
      format.xml  { render :xml => nil }
    end
  end
end
