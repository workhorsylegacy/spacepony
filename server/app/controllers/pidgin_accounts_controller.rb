class PidginAccountsController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []

  # GET /pidgin_accounts
  # GET /pidgin_accounts.json
  def index
    @pidgin_accounts = PidginAccount.find(:all)

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
    @users = User.find(:all)

    respond_to do |format|
      format.html # new.html.erb
      format.json  { render :json => @pidgin_account }
      format.xml  { render :xml => @pidgin_account }
    end
  end

  # GET /pidgin_accounts/1/edit
  def edit
    @pidgin_account = PidginAccount.find(params[:id])
    @users = User.find(:all)
  end

  # POST /pidgin_accounts
  # POST /pidgin_accounts.json
  def create
    @pidgin_account = PidginAccount.new(params[:pidgin_account])

    respond_to do |format|
      if @pidgin_account.save
        flash[:notice] = 'Pidgin Account was successfully created.'
        format.html { redirect_to(@pidgin_account) }
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

    respond_to do |format|
      if @pidgin_account.update_attributes(params[:pidgin_account])
        flash[:notice] = 'Pidgin Account was successfully updated.'
        format.html { redirect_to(@pidgin_account) }
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
      format.html { redirect_to(pidgin_accounts_url) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end
end
