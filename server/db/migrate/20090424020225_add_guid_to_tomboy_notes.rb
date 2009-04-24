class AddGuidToTomboyNotes < ActiveRecord::Migration
  def self.up
    add_column :tomboy_notes, :guid, :string
  end

  def self.down
    remove_column :tomboy_notes, :guid
  end
end
