

class User < ActiveRecord::Base
	has_many :pidgin_accounts

	validates_uniqueness_of :name, :email, :message => "is already used by another user"
	validates_presence_of :name, :email, :message => 'is required'
	validates_length_of :name, :in => 2..30, :allow_blank => :true

	attr_accessor :password
	attr_accessor :password_confirmation
	validate :password_is_valid

	def self.authenticate(name, password)
		user = self.find_by_user_name(name)
		if user
			expected_password = User.encrypt_password(password, user.salt)
			if user.hashed_password != expected_password
				user = nil
			end
		end
		user
	end

	def password
		@password
	end

	def password=(value)
		@password = value
		return if value.blank?
		create_new_salt
		self.hashed_password = User.encrypt_password(self.password, self.salt)
	end


	private

	def password_is_valid
		# Just return if there was previous error
		return if errors['password'] != nil && errors['password'].length > 0

		# Skip validation if there are no changes
		return if self.id != nil && password.blank? && password_confirmation.blank?

		# Do password validation
		if password_confirmation != password
			errors.add('password', "does not match")
		elsif password.length < 8
			errors.add('password', "must be at least 8 characters long")
		elsif hashed_password.blank?
			errors.add('password', "is required")
		end
	end

	def self.encrypt_password(password, salt)
		Base64.encode64(Crypt.encrypt(password + salt))
	end

	def self.decrypt_password(hashed_password, salt)
		len = salt.length
		b = Base64.decode64(hashed_password)
		Crypt.decrypt(b)[0..-(len+1)]
	end

	def create_new_salt
		self.salt = self.object_id.to_s + rand.to_s
	end
end
