class CreateTomboyNotes < ActiveRecord::Migration
  def self.up
    create_table :tomboy_notes do |t|
      t.integer :user_id, :null => false, :default => nil
      t.string :name, :null => false
      t.text :body, :null => false
      t.text :tag

      t.timestamps
    end
  end

  def self.down
    drop_table :tomboy_notes
  end
end
