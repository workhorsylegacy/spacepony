

class TomboyNote < ActiveRecord::Base
	belongs_to :user

	validates_presence_of :user_id, :name, :body, :guid, :message => 'is required'
end
