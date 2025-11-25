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

install_dependencies() {
	echo "Installing dependencies"

	if [ "TRUE" == "${UPGRADE_PACKAGES}" ] ; then
		echo "Upgrading packages"
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

remove_docker_containers() {
	local containers_json=""
	local container_ids=""

	if [ "TRUE" != "${CONTAINER_REMOVE_ENABLED}" ] ; then
		return
	fi

	containers_json="$(sudo docker container ps -a --format json)"
	if [ "" != "${container_ids}" ] ; then
		echo "Removing all Docker containers"
		container_ids="$(echo ${containers_json}
			| jq '.ID' \
			| tr '\n' ' ' \
			| tr -d \")"
		sudo docker container rm ${container_ids} \
			|| error_exit "Failed to remove docker containers: ${container_ids}"
	fi
}

clean_host_state() {
	local caddy_processes=""

	echo "Cleaning host state"

	caddy_processes="$(ps aux | grep -v grep | grep -i caddy)" || true
	if [ "" != "${caddy_processes}" ] ; then
		echo "Signaling already running Caddy"
		sudo pkill caddy || error_exit "Failed to signal Caddy"
	fi

	remove_docker_containers
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
	source ./config.sh

	echo "Deploying to production"

	install_dependencies

	clean_host_state

	deploy_application

	echo "Done deploying to production"
}

main "${@}"
