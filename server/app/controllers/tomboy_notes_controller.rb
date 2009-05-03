
require 'base64'

class TomboyNotesController < ApplicationController
  layout 'default'
  protect_from_forgery :only => []

  # GET /tomboy_notes
  # GET /tomboy_notes.json
  def index
    @tomboy_notes = TomboyNote.find(:all)

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
    @users = User.find(:all)

    respond_to do |format|
      format.html # new.html.erb
      format.json  { render :json => @tomboy_note }
      format.xml  { render :xml => @tomboy_note }
    end
  end

  # GET /tomboy_notes/1/edit
  def edit
    @tomboy_note = TomboyNote.find(params[:id])
    @users = User.find(:all)
  end

  # POST /tomboy_notes
  # POST /tomboy_notes.json
  def create
    @tomboy_note = TomboyNote.new(params[:tomboy_note])

    # Set the initial timestamp
    timestamp = Time.now.to_f
    @tomboy_note.created_timestamp = timestamp
    @tomboy_note.updated_timestamp = timestamp

    respond_to do |format|
      if @tomboy_note.save
        flash[:notice] = 'Tomboy Note was successfully created.'
        format.html { redirect_to(@tomboy_note) }
        format.json  { render :json => @tomboy_note, :status => :created, :location => @tomboy_note }
        format.xml  { render :xml => @tomboy_note, :status => :created, :location => @tomboy_note }
      else
        @users = User.find(:all)
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

    # Set the new updated timestamp
    params[:tomboy_note][:updated_timestamp] = Time.now.to_f

    respond_to do |format|
      if @tomboy_note.update_attributes(params[:tomboy_note])
        flash[:notice] = 'Tomboy Note was successfully updated.'
        format.html { redirect_to(@tomboy_note) }
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
      format.html { redirect_to(tomboy_notes_url) }
      format.json  { head :ok }
      format.xml  { head :ok }
    end
  end

  # GET /tomboy_notes/all_note_meta_data
  # GET /tomboy_notes/all_note_meta_data.json
  def all_note_meta_data
    @data = {}
    TomboyNote.find(:all).each do |n|
        @data['guid-' + n.guid] = { :id => n.id, 
                          :updated_timestamp => n.updated_timestamp}
    end

    respond_to do |format|
      format.html # all_note_meta_data.html.erb
      format.json  { render :json => @data }
      format.xml  { render :xml => @data }
    end
  end

  def get_newer
    newest_updated_timestamp = params['newest_updated_timestamp'].to_f

    @tomboy_notes = TomboyNote.find(:all, :conditions => ['updated_timestamp > ?', newest_updated_timestamp])

    respond_to do |format|
      format.html # get_newer.html.erb
      format.json  { render :json => @tomboy_notes }
      format.xml  { render :xml => @tomboy_notes }
    end
  end
end
