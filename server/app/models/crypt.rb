
require 'ezcrypto'

class Crypt
	CONFIG = YAML.load_file(RAILS_ROOT +
				'/config/crypt.yml')[ENV['RAILS_ENV']].symbolize_keys

	def self.encrypt(field)
		key.encrypt field
	end

	def self.decrypt(field)
		key.decrypt field
	end

	def self.key
		EzCrypto::Key.with_password(CONFIG[:master_key], CONFIG[:salt])
	end
end
