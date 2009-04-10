class CreatePidginAccounts < ActiveRecord::Migration
  def self.up
    create_table :pidgin_accounts do |t|
      t.integer :user_id, :null => false, :default => nil
      t.string :name, :null => false, :default => ''
      t.string :hashed_password, :null => false, :default => ''
      t.string :salt, :null => false
      t.string :status, :null => false, :default => ''
      t.string :message
      t.string :protocol, :null => false, :default => ''
      t.string :icon

      t.timestamps
    end
  end

  def self.down
    drop_table :pidgin_accounts
  end
end
