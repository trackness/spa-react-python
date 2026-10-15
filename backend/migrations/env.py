from alembic import context

from app.database import Base, database_engine
from app.settings import Settings

engine = database_engine(Settings().database_file)
with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        # SQLite alters most of a table only by rebuilding it
        render_as_batch=True,
        # a failed migration rolls back whole, not leaving a rebuild half done
        transactional_ddl=True,
    )
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()
