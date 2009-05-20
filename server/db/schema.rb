# This file is auto-generated from the current state of the database. Instead of editing this file, 
# please use the migrations feature of Active Record to incrementally modify your database, and
# then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your database schema. If you need
# to create the application database on another system, you should be using db:schema:load, not running
# all the migrations from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20090517074259) do

  create_table "bins", :force => true do |t|
    t.integer "user_id",           :limit => 11,                                                 :null => false
    t.string  "file_name",                                                       :default => "", :null => false
    t.string  "server_name",                                                     :default => "", :null => false
    t.string  "file_type",                                                       :default => "", :null => false
    t.string  "mime_type",                                                       :default => "", :null => false
    t.decimal "created_timestamp",               :precision => 20, :scale => 10
    t.decimal "updated_timestamp",               :precision => 20, :scale => 10
  end

  create_table "pidgin_accounts", :force => true do |t|
    t.integer "user_id",           :limit => 11,                                                 :null => false
    t.string  "name",                                                            :default => "", :null => false
    t.string  "hashed_password",                                                 :default => "", :null => false
    t.string  "salt",                                                                            :null => false
    t.string  "status",                                                          :default => "", :null => false
    t.string  "message"
    t.string  "protocol",                                                        :default => "", :null => false
    t.string  "icon"
    t.decimal "created_timestamp",               :precision => 20, :scale => 10
    t.decimal "updated_timestamp",               :precision => 20, :scale => 10
  end

  create_table "tomboy_notes", :force => true do |t|
    t.integer "user_id",           :limit => 11,                                 :null => false
    t.string  "name",                                                            :null => false
    t.text    "body",                                                            :null => false
    t.text    "tag"
    t.string  "guid"
    t.decimal "created_timestamp",               :precision => 20, :scale => 10
    t.decimal "updated_timestamp",               :precision => 20, :scale => 10
  end

  create_table "users", :force => true do |t|
    t.string   "name",                          :default => "", :null => false
    t.string   "hashed_password",               :default => "", :null => false
    t.string   "salt",                                          :null => false
    t.string   "email",                         :default => "", :null => false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "avatar_id",       :limit => 11
    t.integer  "background_id",   :limit => 11
  end

end
