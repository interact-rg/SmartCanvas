#!/bin/bash

set -e

# TODO test
# TODO consider renaming to production_start.sh
# TODO consider splitting to separate init and start scripts

cd $(dirname $0)

readonly IMAGE_BACKEND_NAME="smartcanvas_backend"
readonly IMAGE_BACKEND_TAG="latest"
readonly DOCKER_IMAGE_BACKEND="${IMAGE_BACKEND_NAME}:${IMAGE_BACKEND_TAG}"

error_exit() {
	echo "${1}"
	exit 1
}

install_dependencies() {
	echo "Installing dependencies"

	if [ "TRUE" == "${UPGRADE_PACKAGES}" ] ; then
		echo "Upgrading packages"
		sudo apt update
		sudo apt -y upgrade
	fi

	if [ "" == "$(which etckeeper 2> /dev/null)" ] ; then
		echo "Installing etckeeper"
		sudo apt -y install etckeeper
	fi

	if [ "" == "$(which jq 2> /dev/null)" ] ; then
		echo "Installing jq"
		sudo apt -y install jq
	fi

	if [ "" == "$(which npm 2> /dev/null)" ] ; then
		echo "Installing npm"
		sudo apt -y install npm
	fi

	if [ "" == "$(which docker 2> /dev/null)" ] ; then
		echo "Installing Docker"
		./install_docker.sh
	fi

	if [ "" == "$(which caddy 2> /dev/null)" ] ; then
		echo "Installing Caddy"
		./install_caddy.sh
	fi
}

remove_docker_containers() {
	local containers_json=""
	local container_ids=""

	if [ "TRUE" != "${CONTAINER_REMOVE_ENABLED}" ] ; then
		return
	fi

	containers_json="$(sudo docker container ps -a --format json)"
	if [ "" != "${container_ids}" ] ; then
		echo "Removing all Docker containers"
		container_ids="$(echo ${containers_json} \
			| jq '.ID' \
			| tr '\n' ' ' \
			| tr -d \")"
		sudo docker container rm ${container_ids} \
			|| error_exit "Failed to remove docker containers: ${container_ids}"
	fi
}

terminate_running_caddy() {
	if ps -C caddy ; then
		echo "Signaling already running Caddy"
		sudo pkill caddy || error_exit "Failed to signal Caddy"
	fi
}

clean_host_state() {
	echo "Cleaning host state"

	terminate_running_caddy

	remove_docker_containers
}

assert_frontend_build_variant() {
	local -r build_variants="${BUILD_VARIANT_CONSENT_ON} ${BUILD_VARIANT_CONSENT_OFF}"
	local -r variant_candidate="${1}"

	for variant in ${build_variants} ; do
		if [[ "${FRONTEND_BUILD_VARIANT}" == "${variant}" ]] ; then
			return
		fi
	done

	error_exit "Unknown build variant: ${variant_candidate}"
}

invoke_npm_build() {
	echo "Selected build variant: ${FRONTEND_BUILD_VARIANT}"

	assert_frontend_build_variant "${FRONTEND_BUILD_VARIANT}"

	if [ "${BUILD_VARIANT_CONSENT_OFF}" == "${FRONTEND_BUILD_VARIANT}" ] ; then
		npm run build
		return
	fi

	if [ "${BUILD_VARIANT_CONSENT_ON}" == "${FRONTEND_BUILD_VARIANT}" ] ; then
		npm run build-consent
		return
	fi
}

build_frontend_application_bundle() {
	echo "Building application bundle (to web/static) from frontend sources."

	pushd ../../smartcanvas-frontend/

	npm install

	invoke_npm_build

	popd # ../../smartcanvas-frontend/
}

build_backend_docker_image() {
	local ret

	pushd ../../

	ret=0
	sudo docker image ls --format json \
		| grep "${IMAGE_BACKEND_NAME}" \
		| grep -q "${IMAGE_BACKEND_TAG}" \
		|| ret=$?
	if [ "0" != "${ret}" ] ; then
		echo "Building backend Docker image"
		sudo docker build --file Dockerfile.backend -t "${DOCKER_IMAGE_BACKEND}" . \
			|| error_exit "Failed to build backend Docker image"
	fi

	popd # ../../
}

deploy_application() {
	local -r own_dns_name="${VIRTUAL_MACHINE_DNS_NAME}"
	local -r backend_port="5000"

	echo "Deploying application"

	build_frontend_application_bundle

	build_backend_docker_image

	echo "Caching sudo password"
	sudo echo ""

	echo "Starting backend container"
	nohup sudo docker run \
		-p ${backend_port}:${backend_port} \
		"${DOCKER_IMAGE_BACKEND}" \
		&> $(pwd)/backend.log &

	echo "Starting reverse proxy"
	nohup sudo caddy reverse-proxy \
		--from "${own_dns_name}" \
		--to :${backend_port} \
		&> $(pwd)/caddy.log &
}

main() {
	source ./constants.sh
	source ./config.sh

	echo "Deploying to production"

	echo "Printing config in use"
	cat ./config.sh

	install_dependencies

	clean_host_state

	deploy_application

	echo "Done deploying to production"
}

main "${@}"
