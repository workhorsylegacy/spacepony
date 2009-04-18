

class TomboyNote < ActiveRecord::Base
	belongs_to :user

	validates_presence_of :user_id, :name, :body, :message => 'is required'
end
