

class Bin < ActiveRecord::Base
	has_one :user

	validates_uniqueness_of :file_name, :server_name, :message => "is already used by another file"
	validates_presence_of :file_name, :server_name, :user_id, :mime_type, :file_type, :message => 'is required'

	attr_accessor :body
	attr_accessor :old_server_name

	def get_data()
		File.open('public/' + self.server_name, 'rb') do |f|
			f.read()
		end
	end

	# FIXME: Move the files below the public directory to be hidden
	def self.existing_or_new(user, body, mime_type, original_name, file_type='generic')
		bin = Bin.find(:first, :conditions => ["user_id=? and file_type=?", user.id, file_type])
		bin = Bin.new unless bin

		# Show an error if the file is blank
		if body == nil || body == ""
			errors = bin.errors.instance_variable_get('@errors')
			errors['file'] = [] unless errors['file']
			errors['file'] << "No file was selected"
		end

		# Show an error if the path is blank
		if original_name == nil || original_name == ""
			errors = bin.errors.instance_variable_get('@errors')
			errors['original_path'] = [] unless errors['original_path']
			errors['original_path'] << "No path was selected"
		end

		return bin if bin.errors.length > 0

		bin.body = body
		bin.old_server_name = bin.server_name if bin.id

		# Put the file details into the Bin model
		bin.file_name = original_name
		bin.server_name = "/user_" + file_type + "/" + user.id.to_s + '.' + original_name.split('.').last
		bin.user_id = user.id
		bin.file_type = file_type
		bin.mime_type = mime_type

		# Set the initial timestamp
		timestamp = Time.now.to_f
		bin.created_timestamp = timestamp
		bin.updated_timestamp = timestamp

		return bin
	end

	def after_save
		# Delete the old file
		if self.old_server_name && File.exist?('public' + self.old_server_name)
			File.delete('public' + self.old_server_name)
		end

		# Make all the directories if they do not exist
		FileUtils.mkdir('public/user_' + self.file_type) unless File.directory?('public/user_' + self.file_type)

		# Save the file to disk
		File.open('public' + self.server_name, "wb") do |f|
			f.write(self.body)
		end
	end

	def self.to_nil_xml
		"<bin nil=\"true\"></bin>"
	end
end

