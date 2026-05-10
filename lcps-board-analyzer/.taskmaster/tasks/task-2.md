# Task 2: Database schema: SQLAlchemy models and Alembic migrations

**Status:** pending
**Priority:** high
**Dependencies:** 1

## Description
Define all 6 ORM models and run Alembic migrations to create the schema in PostgreSQL, including the full-text search trigger on agenda_items.

## Implementation Details
1. Verify all 6 models exist in `backend/app/models/`: Source, SeenDocument, Meeting, AgendaItem, SupportingDocument, PipelineRun
2. Confirm `AgendaItem` has the `search_vector` TSVECTOR column with a GIN index
3. Run `alembic revision --autogenerate -m 'initial_schema'` from `backend/`
4. Open the generated migration file and add the PostgreSQL full-text search trigger:
   ```sql
   CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
   BEGIN
     NEW.search_vector := to_tsvector('english',
       coalesce(NEW.title, '') || ' ' ||
       coalesce(NEW.summary, '') || ' ' ||
       coalesce(array_to_string(NEW.decisions, ' '), ''));
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER agenda_items_search_vector_update
     BEFORE INSERT OR UPDATE ON agenda_items
     FOR EACH ROW EXECUTE FUNCTION update_search_vector();
   ```
5. Run `alembic upgrade head`
6. Seed the `sources` table with two rows:
   - LCPS: name='LCPS Board', url='https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public', source_type='lcps', scraper_class='LCPSScraper'
   - Loudoun BOS: name='Loudoun BOS', url='https://webapi.legistar.com/v1/loudoun/events', source_type='loudoun_bos', scraper_class='LegistarScraper'
7. Verify schema: `psql ... -c '\dt'` should list all 6 tables

## Test Strategy
Run `alembic current` — shows head. `SELECT COUNT(*) FROM sources` returns 2. `\d agenda_items` shows search_vector column and trigger exists.
