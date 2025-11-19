#!/bin/bash

set -ex

cd $(dirname $0)

readonly UPGRADE_PACKAGES="TRUE"

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
		sudo apt update
		sudo apt upgrade
	fi

	if [ "" == "$(which etckeeper 2> /dev/null)" ] ; then
		echo "Installing etckeeper"
		sudo apt install etckeeper
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

clean_host_state() {
	local caddy_processes=""
	local container_ids=""

	echo "Cleaning host state"

	caddy_processes="$(ps aux | grep -v grep | grep -i caddy)" || true
	if [ "" != "${caddy_processes}" ] ; then
		echo "Signaling already running Caddy"
		sudo pkill caddy || error_exit "Failed to signal Caddy"
	fi

	container_ids="$(sudo docker container ps -a | cut -f 1 -d ' ' | grep -v CONTAINER)" || true
	if [ "" != "${container_ids}" ] ; then
		echo "Removing all Docker containers"
		sudo docker container rm "${container_ids}" \
			|| error_exit "Failed to remove docker containers: ${container_ids}"
	fi
}

build_backend_docker_image() {
	local -r match_backend_image="${IMAGE_BACKEND_NAME}[[:space:]]+${IMAGE_BACKEND_TAG}"

	pushd ..

	if ! $(sudo docker image ls | grep -q -E "${match_backend_image}") ; then
		echo "Building backend Docker image"
		sudo docker build --file Dockerfile.backend -t "${DOCKER_IMAGE_BACKEND}" . \
			|| error_exit "Failed to build backend Docker image"
	fi

	popd # ..
}

deploy_application() {
	local -r own_dns_name="${VIRTUAL_MACHINE_DNS_NAME}"
	local -r backend_port="5000"

	echo "Deploying application"

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
	echo "Deploying to production"

	install_dependencies

	clean_host_state

	deploy_application
}

main "${@}"
