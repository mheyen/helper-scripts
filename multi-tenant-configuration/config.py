# Configuration

# Set this to your global admin node
base_url = "http://localhost:8080"

# If you have multiple tenants use an URL pattern. # ToDo otherwise, this can be empty or commented out
# example: tenant_url_pattern = "https://{}.example.org"
tenant_url_pattern = "http://{}:8080"

# ToDo You can also define a dictionary of tenant URLs, which will be prioritized over the URL pattern:
# # example:
# tenant_urls = { '<tenant1.id>': 'http://tenant1:8080', '<tenant1.id>': 'http://tenant2:8080' }
# tenant_urls = {
#     'tenant1': 'http://tenant1:8080',
#     'tenant2': 'http://tenant2:8080'
# }

# digest user
digest_user = "opencast_system_account"
digest_pw = "CHANGE_ME"

# path to environment configuration file
env_path = "environment/{}/opencast-organizations.yml"
# path to group configuration file
group_path = "configurations/group_configuration.yaml"