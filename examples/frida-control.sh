#!/system/bin/sh
set -eu
BASE=/data/local/k70-ctf
BIN="$BASE/bin/frida-server-17.26.3"
PIDFILE="$BASE/run/frida.pid"
is_running() {
    [ -r "$PIDFILE" ] || return 1
    pid=$(cat "$PIDFILE")
    case "$pid" in ''|*[!0-9]*) return 1;; esac
    [ -r "/proc/$pid/cmdline" ] || return 1
    grep -q 'frida-server-17.26.3' "/proc/$pid/cmdline"
}
case "${1:-status}" in
    start)
        if is_running; then echo "Frida already running: $pid"; exit 0; fi
        mkdir -p "$BASE/run" "$BASE/logs"
        nohup "$BIN" --listen 127.0.0.1:27042 >"$BASE/logs/frida-server.log" 2>&1 </dev/null &
        echo "$!" >"$PIDFILE"
        sleep 1
        is_running || { cat "$BASE/logs/frida-server.log"; exit 1; }
        echo "Frida running: $pid, listening on 127.0.0.1:27042"
        ;;
    stop)
        if is_running; then kill "$pid"; echo "Frida stopped: $pid"; fi
        rm -f "$PIDFILE"
        ;;
    status)
        if is_running; then echo "Frida running: $pid"; else echo "Frida stopped"; fi
        ;;
    *) echo "Usage: frida-ctl start|stop|status"; exit 2;;
esac
