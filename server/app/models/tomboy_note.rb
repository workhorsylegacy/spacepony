

class TomboyNote < ActiveRecord::Base
	belongs_to :user

	validates_presence_of :user_id, :name, :body, :guid, :message => 'is required'

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
				'guid' => retval['guid'], 
				'user_id' => retval['user_id'], 
				'created_timestamp' => retval['created_timestamp'], 
				'updated_timestamp' => retval['updated_timestamp'] }
	end

	def filtered_attributes
		self.attributes.to_hash
	end
end
