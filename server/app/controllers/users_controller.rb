class UsersController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []
  before_filter :authenticate, :except => [ 'ensure_user_exists', 'new', 'create', 'login' ]

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

  def avatar
    @user = User.find(params[:id])

    return if request.get?

    @bin = Bin.existing_or_new(@user, params['file'], params['original_path'], 'avatar')

    # Save the file and user
    respond_to do |format|
      if @bin.errors.length == 0 && @bin.save && @user.update_attributes(:avatar_id => @bin.id)
        flash[:notice] = "The avatar was successfully saved."
        format.html { redirect_to(:action => "avatar", :id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        format.html { render :action => "avatar", :id => @user.id }
        format.json	{ render :json => @bin.errors, :status => :unprocessable_entity }
        format.xml	{ render :xml => @bin.errors, :status => :unprocessable_entity }
      end
    end
  end

  def background
    @user = User.find(params[:id])

    return if request.get?

    @bin = Bin.existing_or_new(@user, params['file'], params['original_path'], 'background')

    # Save the file and user
    respond_to do |format|
      if @bin.errors.length == 0 && @bin.save && @user.update_attributes(:background_id => @bin.id)
        flash[:notice] = "The background was successfully saved."
        format.html { redirect_to(:action => "background", :id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        format.html { render :action => "background", :id => @user.id }
        format.json	{ render :json => @bin.errors, :status => :unprocessable_entity }
        format.xml	{ render :xml => @bin.errors, :status => :unprocessable_entity }
      end
    end
  end

  def login
    return unless request.post?

    if logg_in(params['user_name'], params['password'])
      redirect_to(:controller => :users, :action => 'show', :id => session[:user_id])
    else
      flash[:notice] = 'Invalid user name or password.'
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
end
