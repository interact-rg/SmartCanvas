terminate_running_caddy() {
	if ps -C caddy ; then
		echo "Signaling already running Caddy"
		sudo pkill caddy || error_exit "Failed to signal Caddy"
	fi
}
