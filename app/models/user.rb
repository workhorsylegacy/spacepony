

class User < ActiveRecord::Base
	has_many :pidgin_accounts

	validates_uniqueness_of :name, :email, :message => "is already used by another user"
	validates_presence_of :user_id, :name, :status, :protocol, :message => 'is required'
	validates_length_of :name, :in => 2..30, :allow_blank => :true
end
