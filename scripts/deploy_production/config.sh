readonly CONTAINER_REMOVE_ENABLED="TRUE"
readonly IMAGE_REMOVE_ENABLED="TRUE"
readonly UPGRADE_PACKAGES="FALSE"

# See variant options from constants.sh
readonly FRONTEND_BUILD_VARIANT="${BUILD_VARIANT_CONSENT_ON}"

# https://docs.csc.fi/cloud/pouta/additional-services/#custom-dns-name
#
# It is not recommended to use predefined fip-XXX... DNS names in
# production.
readonly VIRTUAL_MACHINE_DNS_NAME=""
