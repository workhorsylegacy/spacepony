

class FirefoxBookmarksController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []
  before_filter :authenticate
  before_filter :authorize_originating_user_only, :only => ['index', 'show', 'create', 'update', 'destroy']

  # GET /firefox_bookmarks
  # GET /firefox_bookmarks.xml
  def index
    @user = User.find(params[:user_id])
    @firefox_bookmarks = FirefoxBookmark.find(:all, :conditions => ['user_id=?', @user.id])

    respond_to do |format|
      format.html # index.html.erb
      format.xml  { render :xml => @firefox_bookmarks }
      format.xml  { render :xml => @firefox_bookmarks }
    end
  end

  # GET /firefox_bookmarks/1
  # GET /firefox_bookmarks/1.xml
  def show
    @firefox_bookmark = FirefoxBookmark.find(params[:id])
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # show.html.erb
      format.xml  { render :xml => @firefox_bookmark }
      format.xml  { render :xml => @firefox_bookmark }
    end
  end

  # GET /firefox_bookmarks/new
  # GET /firefox_bookmarks/new.xml
  def new
    @firefox_bookmark = FirefoxBookmark.new
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # new.html.erb
      format.xml  { render :xml => @firefox_bookmark }
      format.xml  { render :xml => @firefox_bookmark }
    end
  end

  # GET /firefox_bookmarks/1/edit
  def edit
    @firefox_bookmark = FirefoxBookmark.find(params[:id])
    @user = User.find(params[:user_id])
  end

  # POST /firefox_bookmarks
  # POST /firefox_bookmarks.xml
  def create
    @firefox_bookmark = FirefoxBookmark.new(params[:firefox_bookmark])
    @user = User.find(params[:firefox_bookmark][:user_id])

    # Set the initial timestamp
    timestamp = Time.now.to_f
    @firefox_bookmark.created_timestamp = timestamp
    @firefox_bookmark.updated_timestamp = timestamp

    respond_to do |format|
      if @firefox_bookmark.save
        flash[:notice] = 'Firefox Bookmark was successfully created.'
        format.html { redirect_to(:action => :show, :id => @firefox_bookmark.id, :user_id => @user.id) }
        format.json  { render :json => @firefox_bookmark, :status => :created, :location => @firefox_bookmark }
        format.xml  { render :xml => @firefox_bookmark, :status => :created, :location => @firefox_bookmark }
      else
        format.html { render :action => "new" }
        format.json  { render :json => @firefox_bookmark.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @firefox_bookmark.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /firefox_bookmarks/1
  # PUT /firefox_bookmarks/1.xml
  def update
    @firefox_bookmark = FirefoxBookmark.find(params[:id])
    @user = User.find(params[:firefox_bookmark][:user_id])

    # Set the new updated timestamp
    params[:firefox_bookmark][:updated_timestamp] = Time.now.to_f

    respond_to do |format|
      if @firefox_bookmark.update_attributes(params[:firefox_bookmark])
        flash[:notice] = 'Firefox Bookmark was successfully updated.'
        format.html { redirect_to(:action => :update, :id => @firefox_bookmark.id, :user_id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        @users = User.find(:all)
        format.html { render :action => "edit" }
        format.json  { render :json => @firefox_bookmark.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @firefox_bookmark.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /firefox_bookmarks/1
  # DELETE /firefox_bookmarks/1.xml
  def destroy
    @firefox_bookmark = FirefoxBookmark.find(params[:id])
    @firefox_bookmark.destroy

    respond_to do |format|
      format.html { redirect_to(:action => :index, :user_id => @firefox_bookmark.user_id) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end

  private

  def get_originating_user_id
    id = if params.has_key? :firefox_bookmark
      params[:firefox_bookmark][:user_id]
    elsif params.has_key? :user_id
      params[:user_id]
    elsif params.has_key? :id
        FirefoxBookmark.find(params[:id]).user_id
    end

    User.find(id).id
  end
end
