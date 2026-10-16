# The App runs as the PUID and PGID its container is given

The Image's entrypoint runs as root only long enough to give the database's directory, the database and SQLite's -wal, -shm and -journal files to the PUID and PGID its container is given, 1000 when unset or empty, then execs the App as them. Whoever runs the Image can therefore match the App to whichever host user owns its volume or bind mount, and change that user later, without re-owning the database by hand. Started by `docker run --user` as any user but root, the entrypoint skips that step and the App runs as that user.

## Considered Options

- **A fixed `USER` in the Image**: the App cannot write a volume or bind mount another user owns, so whoever runs the Image as a different host user re-owns the database by hand.

## Consequences

- The App owns the database's directory, so the entrypoint, started as root, changes a link there itself, never the file it points to, and refuses to start unless the database's path names a file, in an absolute directory other than `/` reached with no link, `.`, `..` or repeated `/`.
- The entrypoint, started as root, creates the database's directory if it is missing. The Image creates its default `/data` writable by any user, so a `docker run --user` App can create its database there; any other directory must already exist and be writable by that user.
- Under a `docker run --user` other than root or an earlier run's PUID, the App cannot write the database files that run left, since nothing re-owns them.
