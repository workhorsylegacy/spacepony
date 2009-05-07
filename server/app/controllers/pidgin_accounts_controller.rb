class PidginAccountsController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []
  before_filter :authenticate
  before_filter :authorize_originating_user_only, :only => ['index', 'show', 'create', 'update', 'destroy']

  # GET /pidgin_accounts
  # GET /pidgin_accounts.json
  def index
    @user = User.find(params[:user_id])
    @pidgin_accounts = PidginAccount.find(:all, :conditions => ['user_id=?', @user.id])

    respond_to do |format|
      format.html # index.html.erb
      format.json  { render :json => @pidgin_accounts }
      format.xml  { render :xml => @pidgin_accounts }
    end
  end

  # GET /pidgin_accounts/1
  # GET /pidgin_accounts/1.json
  def show
    @pidgin_account = PidginAccount.find(params[:id])
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # show.html.erb
      format.json  { render :json => @pidgin_account }
      format.xml  { render :xml => @pidgin_account }
    end
  end

  # GET /pidgin_accounts/new
  # GET /pidgin_accounts/new.json
  def new
    @pidgin_account = PidginAccount.new
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # new.html.erb
      format.json  { render :json => @pidgin_account }
      format.xml  { render :xml => @pidgin_account }
    end
  end

  # GET /pidgin_accounts/1/edit
  def edit
    @pidgin_account = PidginAccount.find(params[:id])
    @user = User.find(params[:user_id])
  end

  # POST /pidgin_accounts
  # POST /pidgin_accounts.json
  def create
    @pidgin_account = PidginAccount.new(params[:pidgin_account])
    @user = User.find(params[:pidgin_account][:user_id])

    # Set the initial timestamp
    timestamp = Time.now.to_f
    @pidgin_account.created_timestamp = timestamp
    @pidgin_account.updated_timestamp = timestamp

    respond_to do |format|
      if @pidgin_account.save
        flash[:notice] = 'Pidgin Account was successfully created.'
        format.html { redirect_to(:action => :show, :id => @pidgin_account.id, :user_id => @user.id) }
        format.json  { render :json => @pidgin_account, :status => :created, :location => @pidgin_account }
        format.xml  { render :xml => @pidgin_account, :status => :created, :location => @pidgin_account }
      else
        @users = User.find(:all)
        format.html { render :action => "new" }
        format.json  { render :json => @pidgin_account.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @pidgin_account.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /pidgin_accounts/1
  # PUT /pidgin_accounts/1.json
  def update
    @pidgin_account = PidginAccount.find(params[:id])
    @user = User.find(params[:pidgin_account][:user_id])

    # Set the new updated timestamp
    params[:pidgin_account][:updated_timestamp] = Time.now.to_f

    respond_to do |format|
      if @pidgin_account.update_attributes(params[:pidgin_account])
        flash[:notice] = 'Pidgin Account was successfully updated.'
        format.html { redirect_to(:action => :update, :id => @pidgin_account.id, :user_id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        @users = User.find(:all)
        format.html { render :action => "edit" }
        format.json  { render :json => @pidgin_account.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @pidgin_account.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /pidgin_accounts/1
  # DELETE /pidgin_accounts/1.json
  def destroy
    @pidgin_account = PidginAccount.find(params[:id])
    @pidgin_account.destroy

    respond_to do |format|
      format.html { redirect_to(:action => :index, :user_id => @pidgin_account.user_id) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end

  # GET /pidgin_accounts/all_account_meta_data
  # GET /pidgin_accounts/all_account_meta_data.json
  def all_note_meta_data
    @data = {}
    PidginAccount.find(:all, :conditions => ['user_id=?', params[:user_id]]).each do |n|
        @data[n.name + ':' + n.protocol] = { :id => n.id, 
                          :updated_timestamp => n.updated_timestamp}
    end

    respond_to do |format|
      format.html # all_note_meta_data.html.erb
      format.json  { render :json => @data }
      format.xml  { render :xml => @data }
    end
  end

  def get_newer
    newest_timestamp = params['newest_timestamp'].to_f

    @pidgin_accounts = PidginAccount.find(:all, :conditions => ['user_id=? and updated_timestamp>?', 
                                                          params[:user_id], 
                                                          newest_timestamp])

    respond_to do |format|
      format.html # get_newer.html.erb
      format.json  { render :json => @pidgin_accounts }
      format.xml  { render :xml => @pidgin_accounts }
    end
  end

  private

  def get_originating_user_id
    id = if params.has_key? :pidgin_account
      params[:pidgin_account][:user_id]
    else
      params[:user_id]
    end

    User.find(id).id
  end
end
