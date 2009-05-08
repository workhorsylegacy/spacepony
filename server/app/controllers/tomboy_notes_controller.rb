
require 'base64'

class TomboyNotesController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []
  before_filter :authenticate
  before_filter :authorize_originating_user_only, :only => ['index', 'show', 'create', 'update', 'destroy', 'all_note_meta_data', 'get_newer']

  # GET /tomboy_notes
  # GET /tomboy_notes.json
  def index
    @user = User.find(params[:user_id])
    @tomboy_notes = TomboyNote.find(:all, :conditions => ['user_id=?', @user.id])

    respond_to do |format|
      format.html # index.html.erb
      format.json  { render :json => @tomboy_notes }
      format.xml  { render :xml => @tomboy_notes }
    end
  end

  # GET /tomboy_notes/1
  # GET /tomboy_notes/1.json
  def show
    @tomboy_note = TomboyNote.find(params[:id])
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # show.html.erb
      format.json  { render :json => @tomboy_note }
      format.xml  { render :xml => @tomboy_note }
    end
  end

  # GET /tomboy_notes/new
  # GET /tomboy_notes/new.json
  def new
    @tomboy_note = TomboyNote.new
    @user = User.find(params[:user_id])

    respond_to do |format|
      format.html # new.html.erb
      format.json  { render :json => @tomboy_note }
      format.xml  { render :xml => @tomboy_note }
    end
  end

  # GET /tomboy_notes/1/edit
  def edit
    @tomboy_note = TomboyNote.find(params[:id])
    @user = User.find(params[:user_id])
  end

  # POST /tomboy_notes
  # POST /tomboy_notes.json
  def create
    @tomboy_note = TomboyNote.new(params[:tomboy_note])
    @user = User.find(params[:tomboy_note][:user_id])

    # Set the initial timestamp
    timestamp = Time.now.to_f
    @tomboy_note.created_timestamp = timestamp
    @tomboy_note.updated_timestamp = timestamp

    respond_to do |format|
      if @tomboy_note.save
        flash[:notice] = 'Tomboy Note was successfully created.'
        format.html { redirect_to(:action => :show, :id => @tomboy_note.id, :user_id => @user.id) }
        format.json  { render :json => @tomboy_note, :status => :created, :location => @tomboy_note }
        format.xml  { render :xml => @tomboy_note, :status => :created, :location => @tomboy_note }
      else
        format.html { render :action => "new" }
        format.json  { render :json => @tomboy_note.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @tomboy_note.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /tomboy_notes/1
  # PUT /tomboy_notes/1.json
  def update
    @tomboy_note = TomboyNote.find(params[:id])
    @user = User.find(params[:tomboy_note][:user_id])

    # Set the new updated timestamp
    params[:tomboy_note][:updated_timestamp] = Time.now.to_f

    respond_to do |format|
      if @tomboy_note.update_attributes(params[:tomboy_note])
        flash[:notice] = 'Tomboy Note was successfully updated.'
        format.html { redirect_to(:action => :update, :id => @tomboy_note.id, :user_id => @user.id) }
        format.json  { head :ok }
        format.xml  { head :ok }
      else
        @users = User.find(:all)
        format.html { render :action => "edit" }
        format.json  { render :json => @tomboy_note.errors, :status => :unprocessable_entity }
        format.xml  { render :xml => @tomboy_note.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /tomboy_notes/1
  # DELETE /tomboy_notes/1.json
  def destroy
    @tomboy_note = TomboyNote.find(params[:id])
    @tomboy_note.destroy

    respond_to do |format|
      format.html { redirect_to(:action => :index, :user_id => @tomboy_note.user_id) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end

  def get_newer
    newest_timestamp = params['newest_timestamp'].to_f

    @tomboy_notes = TomboyNote.find(:all, :conditions => ['user_id=? and updated_timestamp>?', 
                                                          params[:user_id], 
                                                          newest_timestamp])

    respond_to do |format|
      format.html # get_newer.html.erb
      format.json  { render :json => @tomboy_notes }
      format.xml  { render :xml => @tomboy_notes }
    end
  end

  private

  def get_originating_user_id
    id = if params.has_key? :tomboy_note
      params[:tomboy_note][:user_id]
    elsif params.has_key? :user_id
      params[:user_id]
    elsif params.has_key? :id
        TomboyNote.find(params[:id]).user_id
    end

    User.find(id).id
  end
end
