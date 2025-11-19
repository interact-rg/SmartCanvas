#!/bin/bash

set -ex

cd $(dirname $0)

readonly UPGRADE_PACKAGES="FALSE"

install_dependencies() {
	if [ "TRUE" == "${UPGRADE_PACKAGES}" ] ; then
		sudo apt update
		sudo apt upgrade
	fi

	if [ "" == "$(which etckeeper)" ] ; then
		sudo apt install etckeeper
	fi

	if [ "" == "$(which docker 2> /dev/null)" ] ; then
		echo "Installing Docker"

		./install_docker_apt_repository.sh
		./install_docker_packages.sh
		./run_docker_hello_world.sh
	fi

	if [ "" == "$(which caddy 2> /dev/null)" ] ; then
		echo "Installing Caddy"
		./install_caddy.sh
	fi

}

main() {
	local -r own_dns_name="fip-86-50-20-216.kaj.poutavm.fi"
	local -r image_backend_name="smartcanvas_backend"
	local -r image_backend_tag="latest"
	local -r docker_image_backend="${image_backend_name}:${image_backend_tag}"
	local -r match_backend_image="${image_backend_name}[[:space:]]+${image_backend_tag}"

	local container_ids=""

	install_dependencies

	pushd ..

	if ! $(sudo docker image ls | grep -q -E "${match_backend_image}") ; then
		echo "Building backend Docker image"
		sudo docker build --file Dockerfile.backend -t "${docker_image_backend}" .
	fi

	popd # ..

	container_ids="$(sudo docker container ps -a | cut -f 1 -d ' ' | grep -v CONTAINER)" || true
	if [ "" != "${container_ids}" ] ; then
		echo "Removing all Docker containers"
		sudo docker container rm "${container_ids}"
	fi

	echo "Starting backend container"
	nohup sudo docker run -p 5000:5000 "${docker_image_backend}" &> $(pwd)/backend.log &

	echo "Starting reverse proxy"
	sudo pkill caddy || true
	nohup sudo caddy reverse-proxy --from "${own_dns_name}" --to :5000 &> $(pwd)/caddy.log &
}

main "${@}"
