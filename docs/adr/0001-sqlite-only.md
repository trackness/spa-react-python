# SQLite is the only supported database

Every Project runs as a single instance on a host with a local disk, so the Template supports SQLite alone: the database is a file on the container's volume and the whole Project is one container. PostgreSQL is not supported, tested against, or kept compatible; a Project that outgrows SQLite migrates on its own.

## Considered Options

- **PostgreSQL only**: a second service in every Project for capacity none of them is expected to need.
- **Both, through the ORM**: every Project pays for a switch almost none will make, and an untested "compatible" path rots.

## Consequences

- One writer at a time, and the database file must not live on a network filesystem.
- A Project cannot run more than one instance.
- Most schema changes rebuild the table, so every constraint must be named.
- Copying the database file alone while the app is running can lose committed data.
