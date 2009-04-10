class CreateUsers < ActiveRecord::Migration
  def self.up
    create_table :users do |t|
      t.string :name, :null => false, :default => ''
      t.string :hashed_password, :null => false, :default => ''
      t.string :email, :null => false, :default => ''

      t.timestamps
    end
  end

  def self.down
    drop_table :users
  end
end
