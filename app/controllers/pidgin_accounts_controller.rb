class PidginAccountsController < ApplicationController
  # GET /pidgin_accounts
  # GET /pidgin_accounts.xml
  def index
    @pidgin_accounts = PidginAccount.find(:all)

    respond_to do |format|
      format.html # index.html.erb
      format.xml  { render :xml => @pidgin_accounts }
    end
  end

  # GET /pidgin_accounts/1
  # GET /pidgin_accounts/1.xml
  def show
    @pidgin_account = PidginAccount.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.xml  { render :xml => @pidgin_account }
    end
  end

  # GET /pidgin_accounts/new
  # GET /pidgin_accounts/new.xml
  def new
    @pidgin_account = PidginAccount.new

    respond_to do |format|
      format.html # new.html.erb
      format.xml  { render :xml => @pidgin_account }
    end
  end

  # GET /pidgin_accounts/1/edit
  def edit
    @pidgin_account = PidginAccount.find(params[:id])
  end

  # POST /pidgin_accounts
  # POST /pidgin_accounts.xml
  def create
    @pidgin_account = PidginAccount.new(params[:pidgin_account])

    respond_to do |format|
      if @pidgin_account.save
        flash[:notice] = 'Pidgin Account was successfully created.'
        format.html { redirect_to(@pidgin_account) }
        format.xml  { render :xml => @pidgin_account, :status => :created, :location => @pidgin_account }
      else
        format.html { render :action => "new" }
        format.xml  { render :xml => @pidgin_account.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /pidgin_accounts/1
  # PUT /pidgin_accounts/1.xml
  def update
    @pidgin_account = PidginAccount.find(params[:id])

    respond_to do |format|
      if @pidgin_account.update_attributes(params[:pidgin_account])
        flash[:notice] = 'Pidgin Account was successfully updated.'
        format.html { redirect_to(@pidgin_account) }
        format.xml  { head :ok }
      else
        format.html { render :action => "edit" }
        format.xml  { render :xml => @pidgin_account.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /pidgin_accounts/1
  # DELETE /pidgin_accounts/1.xml
  def destroy
    @pidgin_account = PidginAccount.find(params[:id])
    @pidgin_account.destroy

    respond_to do |format|
      format.html { redirect_to(pidgin_accounts_url) }
      format.xml  { head :ok }
    end
  end
end
