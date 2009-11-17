class CreateFirefoxBookmarks < ActiveRecord::Migration
  def self.up
    create_table :firefox_bookmarks do |t|
      t.integer :user_id, :null => false, :default => nil
      t.string :title, :null => false
      t.string :uri, :null => false
      t.string :guid, :null => false
      t.string :folder, :null => false
      t.decimal :created_timestamp, :precision => 20, :scale => 10
      t.decimal :updated_timestamp, :precision => 20, :scale => 10

      t.timestamps
    end
    remove_column :firefox_bookmarks, :created_at
    remove_column :firefox_bookmarks, :updated_at
  end

  def self.down
    drop_table :firefox_bookmarks
  end
end
