#!/system/bin/sh
set -eu
ROOT=/data/local/k70-ctf/kali-arm64
BB=/data/adb/magisk/busybox
case "${K70_KALI_PRIVATE_NS:-}" in
    1) ;;
    *) HOST_NS=$(readlink /proc/self/ns/mnt)
       exec "$BB" unshare --mount --propagation private /system/bin/env K70_KALI_PRIVATE_NS=1 \
           K70_KALI_HOST_NS="$HOST_NS" /system/bin/sh "$0" "$@";;
esac
if [ "$(readlink /proc/self/ns/mnt)" = "$K70_KALI_HOST_NS" ]; then
    echo 'Kali requires its own mount namespace' >&2
    exit 1
fi
"$BB" mount -o rprivate / /
"$BB" mount -t tmpfs -o mode=755 tmpfs "$ROOT/dev"
mkdir -p "$ROOT/dev/pts" "$ROOT/dev/shm"
"$BB" mknod -m 666 "$ROOT/dev/null" c 1 3
"$BB" mknod -m 666 "$ROOT/dev/zero" c 1 5
"$BB" mknod -m 666 "$ROOT/dev/full" c 1 7
"$BB" mknod -m 666 "$ROOT/dev/random" c 1 8
"$BB" mknod -m 666 "$ROOT/dev/urandom" c 1 9
"$BB" mknod -m 666 "$ROOT/dev/tty" c 5 0
ln -s /proc/self/fd "$ROOT/dev/fd"
ln -s /proc/self/fd/0 "$ROOT/dev/stdin"
ln -s /proc/self/fd/1 "$ROOT/dev/stdout"
ln -s /proc/self/fd/2 "$ROOT/dev/stderr"
ln -s pts/ptmx "$ROOT/dev/ptmx"
"$BB" mount -o bind /dev/pts "$ROOT/dev/pts"
"$BB" mount -t proc proc "$ROOT/proc"
"$BB" mount -t sysfs sysfs "$ROOT/sys"
"$BB" mount -t tmpfs -o mode=1777,size=512m tmpfs "$ROOT/dev/shm"
"$BB" mount -o bind /sdcard "$ROOT/sdcard"
"$BB" mount -o bind /data/local/k70-ctf/samples "$ROOT/root/ctf/samples"
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root USER=root LOGNAME=root SHELL=/bin/bash LANG=C.UTF-8
export TERM="${TERM:-xterm-256color}"
unset LD_PRELOAD LD_LIBRARY_PATH PREFIX
if [ "$#" -eq 0 ]; then
    exec /system/bin/chroot "$ROOT" /bin/bash --login
else
    exec /system/bin/chroot "$ROOT" /usr/bin/env -i HOME=/root USER=root LOGNAME=root \
        PATH="$PATH" LANG=C.UTF-8 TERM="$TERM" "$@"
fi
