#!/bin/bash

set -e

cd $(dirname $0)

stop_docker_containers() {
	local containers_json=""
	local container_ids=""

	containers_json="$(sudo docker container ps -a --format json)"
	if [ "" != "${containers_json}" ] ; then
		echo "Stopping all Docker containers"
		container_ids="$(echo ${containers_json} \
			| jq '.ID' \
			| tr '\n' ' ' \
			| tr -d \")"
		sudo docker container stop ${container_ids} \
			|| error_exit "Failed to stop docker containers: ${container_ids}"
	fi
}

main() {
	source ./common.sh

	stop_docker_containers

	terminate_running_caddy
}

main "${@}"
