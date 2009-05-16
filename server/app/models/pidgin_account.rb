

class PidginAccount < ActiveRecord::Base
	belongs_to :user

	validates_presence_of :user_id, :name, :status, :protocol, :message => 'is required'

	attr_accessor :password
	validate :password_is_valid

	def password
		@password
	end

	def password=(value)
		@password = value
		return if value.blank?
		create_new_salt
		self.hashed_password = PidginAccount.encrypt_password(self.password, self.salt)
	end

	def to_xml(options={})
		if @apply_meta_filter
			meta_attributes.to_xml(options)
		else
			filtered_attributes.to_xml(options)
		end
	end

	def to_json(options={})
		if @apply_meta_filter
			meta_attributes.to_xml(options)
		else
			filtered_attributes.to_json(options)
		end
	end

	def apply_meta_filter()
		@apply_meta_filter = true
	end

	private

	def meta_attributes
		retval = self.attributes.to_hash
		retval = { 'id' => retval['id'], 
				'name' => retval['name'], 
				'protocol' => retval['protocol'], 
				'user_id' => retval['user_id'], 
				'created_timestamp' => retval['created_timestamp'], 
				'updated_timestamp' => retval['updated_timestamp'] }
	end

	def filtered_attributes
		retval = self.attributes.to_hash

		retval['password'] = PidginAccount.decrypt_password(self.hashed_password, self.salt)
		retval.delete('hashed_password')
		retval.delete('salt')

		retval
	end

	def password_is_valid
		# Just return if there was previous error
		return if errors['password'] != nil && errors['password'].length > 0

		# Skip validation if there are no changes
		return if self.id != nil && password.blank?

		# Do password validation
		if hashed_password.blank?
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
