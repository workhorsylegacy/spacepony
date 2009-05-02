class ChangeTomboyNoteDatePrecision < ActiveRecord::Migration
  def self.up
    remove_column :tomboy_notes, :created_at
    remove_column :tomboy_notes, :updated_at
    add_column :tomboy_notes, :created_timestamp, :double
    add_column :tomboy_notes, :updated_timestamp, :double
  end

  def self.down
    remove_column :tomboy_notes, :created_at
    remove_column :tomboy_notes, :updated_at
    add_column :tomboy_notes, :created_timestamp, :decimal
    add_column :tomboy_notes, :updated_timestamp, :decimal
  end
end
