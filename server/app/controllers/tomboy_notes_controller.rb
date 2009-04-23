
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

  # FIXME: Remove this. It is just a test for custom rest methods
  def poop
    @tomboy_notes = TomboyNote.find(:all, :conditions => ["name = ?", params[:name]])

    respond_to do |format|
      format.html # index.html.erb
      format.json  { render :json => @tomboy_notes }
      format.xml  { render :xml => @tomboy_notes }
    end
  end
end
