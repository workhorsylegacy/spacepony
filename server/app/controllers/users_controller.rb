class UsersController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []
  # FIXME: Authentication should be on for avatar and background
  before_filter :authenticate, :except => [ 'ensure_user_exists', 'new', 'create', 'login', 'avatar', 'background' ]

  # GET /users/1
  # GET /users/1.json
  def show
    @user = User.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.json  { render :json => @user }
      format.xml  { render :xml => @user }
    end
  end

  # GET /users/new
  # GET /users/new.json
  def new
    @user = User.new

    respond_to do |format|
      format.html # new.html.erb
      format.json  { render :json => @user }
      format.xml  { render :xml => @user }
    end
  end

  # GET /users/1/edit
  def edit
    @user = User.find(params[:id])
  end

  # POST /users
  # POST /users.json
  def create
    @user = User.new(params[:user])

    respond_to do |format|
      if @user.save
        flash[:notice] = 'User was successfully created.'
        format.html { redirect_to(@user) }
        format.json  { render :json => @user, :status => :created, :location => @user }
        format.xml  { render :xml => @user, :status => :created, :location => @user }
      else
        format.html { render :action => "new" }
        format.json  { render :json => @user.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /users/1
  # PUT /users/1.json
  def update
    @user = User.find(params[:id])

    respond_to do |format|
      if @user.update_attributes(params[:user])
        flash[:notice] = 'User was successfully updated.'
        format.html { redirect_to('login') }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        format.html { render :action => "edit" }
        format.json  { render :json => @user.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /users/1
  # DELETE /users/1.json
  def destroy
    @user = User.find(params[:id])
    @user.destroy

    respond_to do |format|
      format.html { redirect_to(users_url) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end

  # POST /users/1/avatar
  # POST /users/1/avatar.html
  # POST /users/1/avatar.jpeg
  def avatar
    action_for_image_attribute('avatar', params)
  end

  def background
    action_for_image_attribute('background', params)
  end

  def login
    return unless request.post?

    if log_in(params['user_name'], params['password'])
      redirect_to(:controller => :users, :action => 'show', :id => session[:user_id])
    else
      flash[:notice] = 'Invalid user name or password.'
    end
  end

  def logout
    # Remove the sessions and cookies.
    session[:user_id] = nil
    cookies[:user_id] = nil
    cookies[:user_name] = nil
    cookies[:user_greeting] = nil
    flash[:notice] = "You are now logged out."

   # Try to go to the previous page. If there is none, or 
   # it is from a different site, go home.
    from_same_site = was_request_from_this_site?(request)

    if from_same_site
      redirect_to(request.env_table['HTTP_REFERER'])
    else
      redirect_to :controller => 'home', :action => 'index'
    end
  end

  def get_logged_in_user
    @user = User.find(session[:user_id])

    respond_to do |format|
      format.html # get_logged_in_user.html.erb
      format.json  { render :json => @user }
      format.xml  { render :xml => @user }
    end
  end

  def ensure_user_exists
    # Get the params
    name = params['name']
    password = params['password']
    email = params['email']

    # Determine if the user exists and can login
    user_exists = user_exists?(name)
    valid_login = valid_login?(name, password)

    respond_to do |format|
      if user_exists && valid_login
        flash[:notice] = 'User can login.'
        format.html { head :ok }
        format.json  { head :ok }
        format.xml  { head :ok }
      elsif user_exists && valid_login == false
        flash[:notice] = 'Invalid login.'
        format.html { head :unauthorized }
        format.json  { head :unauthorized }
        format.xml  { head :unauthorized }
      elsif user_exists == false
        user = User.new
        user.name = name
        user.email = email
        user.password = password
        user.password_confirmation = password
        if user.save
          flash[:notice] = 'User was created, and can login.'
          format.html { head :ok }
          format.json  { head :ok }
          format.xml  { head :ok }
        else
          format.html { head :unprocessable_entity }
          format.json  { render :json => user.errors, :status => :unprocessable_entity }
          format.xml  { render :xml => user.errors, :status => :unprocessable_entity }
        end
      end
    end
  end

  private

  def action_for_image_attribute(name, params)
    @user = User.find(params[:id])

    if request.get?
      respond_to do |format|
          format.html # name.html.erb
          format.json  { render :json => @user.send(name) }
          format.xml  { render :xml => @user.send(name) || Bin.to_nil_xml }
          format.jpeg { render :text => @user.send(name).get_data() }
          format.jpg { render :text => @user.send(name).get_data() }
          format.jpe { render :text => @user.send(name).get_data() }
          format.gif { render :text => @user.send(name).get_data() }
          format.png { render :text => @user.send(name).get_data() }
          format.svg { render :text => @user.send(name).get_data() }
      end
    end

    if request.delete?
        @user.send(name).destroy()
        respond_to do |format|
          flash[:notice] = "The background was successfully deleted."
          format.html { redirect_to(:action => name, :id => @user.id) }
          format.json  { head :ok }
          format.xml  { head :ok }
          format.jpeg { head :ok }
          format.jpg { head :ok }
          format.jpe { head :ok }
          format.gif { head :ok }
          format.png { head :ok }
          format.svg { head :ok }
        end
        return
    end

    return unless request.post?

    file_body, file_mime_type, file_original_name = nil, nil, nil
    # Get webform posted file
    if params['file'] != nil && params['file'] != ""
      file = params['file']
      file_body = file.read
      file_mime_type = file.content_type.chomp.downcase
      file_original_name = params['original_path'] + file.original_filename
    # Get REST posted file
    else
      file = request.body
      file_body = file.read
      file_mime_type = request.env['CONTENT_TYPE']
      file_original_name = params['original_filename']
    end

    @bin = Bin.existing_or_new(@user, file_body, file_mime_type, file_original_name, name)

    # Save the file and user
    respond_to do |format|
      if @bin.errors.length == 0 && @bin.save && @user.update_attributes(:"#{name}_id" => @bin.id)
        flash[:notice] = "The " + name + " was successfully saved."
        format.html { redirect_to(:action => name, :id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
        format.jpeg { head :ok }
        format.jpg { head :ok }
        format.jpe { head :ok }
        format.gif { head :ok }
        format.png { head :ok }
        format.svg { head :ok }
      else
        format.html { render :action => name, :id => @user.id }
        format.json	{ render :json => @bin.errors, :status => :unprocessable_entity }
        format.xml	{ render :xml => @bin.errors, :status => :unprocessable_entity }
        format.jpeg { head :error }
        format.jpg { head :error }
        format.jpe { head :error }
        format.gif { head :error }
        format.png { head :error }
        format.svg { head :error }
      end
    end
  end

end
