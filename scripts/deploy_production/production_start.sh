#!/bin/bash

set -e

cd $(dirname $0)

readonly IMAGE_BACKEND_NAME="smartcanvas_backend"
readonly IMAGE_BACKEND_TAG="latest"
readonly DOCKER_IMAGE_BACKEND="${IMAGE_BACKEND_NAME}:${IMAGE_BACKEND_TAG}"

error_exit() {
	echo "${1}"
	exit 1
}

validate_config() {
	if [ "" == "${VIRTUAL_MACHINE_DNS_NAME}" ] ; then
		error_exit "Please set a value for VIRTUAL_MACHINE_DNS_NAME in config.sh"
	fi

	if [ "" == "${BACKEND_APP_ENDPOINT}" ] ; then
		error_exit "Please set a value for BACKEND_APP_ENDPOINT in config.sh"
	fi
}

install_dependencies() {
	echo "Installing dependencies"

	if [ "TRUE" == "${UPGRADE_PACKAGES_ENABLED}" ] ; then
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

	if [ "" == "$(command -v nvm)" ] ; then
		echo "Installing nvm"

		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

		export NVM_DIR="$HOME/.nvm"
		[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
		command -v nvm || error_exit "Failed to install nvm"

		echo "Installing LTS node and bundled npm"
		nvm install ${NODEJS_VERSION} \
			|| error_exit "Failed to install node ${NODEJS_VERSION} and bundled npm"
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

remove_docker_images() {
	local images_json=""
	local image_ids=""

	if [ "TRUE" != "${IMAGE_REMOVE_ENABLED}" ] ; then
		return
	fi

	images_json="$(sudo docker image ls --format json)"
	if [ "" != "${images_json}" ] ; then
		echo "Removing all Docker images"
		image_ids="$(echo ${images_json} \
			| jq '.ID' \
			| tr '\n' ' ' \
			| tr -d \")"
		sudo docker image rm ${image_ids} \
			|| error_exit "Failed to remove docker images: ${image_ids}"
	fi
}

remove_docker_containers() {
	local containers_json=""
	local container_ids=""

	if [ "TRUE" != "${CONTAINER_REMOVE_ENABLED}" ] ; then
		return
	fi

	containers_json="$(sudo docker container ps -a --format json)"
	if [ "" != "${containers_json}" ] ; then
		echo "Removing all Docker containers"
		container_ids="$(echo ${containers_json} \
			| jq '.ID' \
			| tr '\n' ' ' \
			| tr -d \")"
		sudo docker container rm ${container_ids} \
			|| error_exit "Failed to remove docker containers: ${container_ids}"
	fi
}

clean_host_state() {
	echo "Cleaning host state"

	terminate_running_caddy

	remove_docker_containers

	remove_docker_images
}

assert_frontend_build_variant() {
	local -r build_variants="${BUILD_VARIANT_CONSENT_ON} ${BUILD_VARIANT_CONSENT_OFF}"
	local -r variant_candidate="${1}"

	for variant in ${build_variants} ; do
		if [ "${FRONTEND_BUILD_VARIANT}" == "${variant}" ] ; then
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

	nvm use ${NODEJS_VERSION} \
		|| error_exit "Failed to select node ${NODEJS_VERSION} using nvm"

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
		sudo docker build \
			--file Dockerfile.backend \
			--build-arg APP_ENDPOINT_TOKEN=${BACKEND_APP_ENDPOINT} \
			-t "${DOCKER_IMAGE_BACKEND}" \
			. \
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
	source ./common.sh

	echo "Validating config"
	validate_config

	echo "Deploying to production"

	echo "Printing the latest commit"
	git show --stat HEAD

	echo "Printing config in use"
	cat ./config.sh

	install_dependencies

	clean_host_state

	deploy_application

	echo "Done deploying to production"
}

main "${@}"
