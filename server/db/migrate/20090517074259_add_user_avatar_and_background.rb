class AddUserAvatarAndBackground < ActiveRecord::Migration
  def self.up
    create_table :bins do |t|
      t.integer :user_id, :null => false
      t.string :file_name, :null => false, :default => ''
      t.string :server_name, :null => false, :default => ''
      t.string :file_type, :null => false, :default => ''
      t.string :mime_type, :null => false, :default => ''

      t.decimal "created_timestamp", :precision => 20, :scale => 10
      t.decimal "updated_timestamp", :precision => 20, :scale => 10
    end

    add_column :users, :avatar_id, :integer
    add_column :users, :background_id, :integer
  end

  def self.down
    drop_table :files

    remove_column :users, :background_id
    remove_column :users, :avatar_id
  end
end
