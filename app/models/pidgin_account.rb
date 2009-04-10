class PidginAccount < ActiveRecord::Base
	belongs_to :user

	validates_presence_of :name, :email, :message => 'is required'
end
