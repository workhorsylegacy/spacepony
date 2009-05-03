class ChangeTomboyNoteDatePrecision < ActiveRecord::Migration
  def self.up
    remove_column :tomboy_notes, :created_at
    remove_column :tomboy_notes, :updated_at
    add_column :tomboy_notes, :created_timestamp, :decimal, :precision => 20, :scale => 10
    add_column :tomboy_notes, :updated_timestamp, :decimal, :precision => 20, :scale => 10
  end

  def self.down
    remove_column :tomboy_timestamp, :created_timestamp
    remove_column :tomboy_timestamp, :updated_timestamp
    add_column :tomboy_notes, :created_at, :datetime
    add_column :tomboy_notes, :updated_at, :datetime
  end
end
