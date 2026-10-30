#!/bin/sh
set -e

# only root can give the database away, so a user Docker starts the Image as runs the App
# as it is (docker run --user)
[ "$(id -u)" = 0 ] || exec "$@"

: "${PUID:=1000}" "${PGID:=1000}"

refuse() {
	echo "APP_DATABASE_FILE must name a file in an absolute directory other than /, with no link, ., .. or repeated / on the way" >&2
	exit 1
}

# the App owns the database's directory, so a link or a relative step on the way to it
# could steer root's chown anywhere: only a file in a canonical directory is taken
directory="${APP_DATABASE_FILE%/*}"
if [ "${directory:-/}" = / ] || [ "$(realpath -m -- "$directory")" != "$directory" ]; then
	refuse
fi
case "${APP_DATABASE_FILE##*/}" in
'' | . | ..) refuse ;;
esac
[ ! -d "$APP_DATABASE_FILE" ] || refuse

mkdir -p "$directory"
chown "$PUID:$PGID" "$directory"
# the App controls what lies in its directory, so a link there may point anywhere
for suffix in '' -wal -shm -journal; do
	file="$APP_DATABASE_FILE$suffix"
	[ ! -e "$file" ] || chown --no-dereference "$PUID:$PGID" "$file"
done

exec setpriv --reuid="$PUID" --regid="$PGID" --clear-groups -- "$@"
