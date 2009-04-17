class CreateTomboyNotes < ActiveRecord::Migration
  def self.up
    create_table :tomboy_notes do |t|
      t.integer :user_id, :null => false, :default => nil
      t.string :name, :null => false
      t.string :body, :null => false
      t.string :tag, :null => false

      t.timestamps
    end
  end

  def self.down
    drop_table :tomboy_notes
  end
end
