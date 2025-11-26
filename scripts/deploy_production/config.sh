CONTAINER_REMOVE_ENABLED="FALSE"
IMAGE_REMOVE_ENABLED="FALSE"
UPGRADE_PACKAGES="TRUE"

# See variant options from constants.sh
FRONTEND_BUILD_VARIANT="${BUILD_VARIANT_CONSENT_ON}"

# https://docs.csc.fi/cloud/pouta/additional-services/#custom-dns-name
#
# It is not recommended to use predefined fip-XXX... DNS names in
# production.
VIRTUAL_MACHINE_DNS_NAME="fip-86-50-20-216.kaj.poutavm.fi"
