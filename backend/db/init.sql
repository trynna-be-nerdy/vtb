-- Auto-update search_vector on agenda_items insert/update.
-- Concatenates title + summary + decisions so full-text search spans all three.

CREATE OR REPLACE FUNCTION update_agenda_search_vector()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.search_vector := to_tsvector(
        'english',
        coalesce(NEW.title, '')   || ' ' ||
        coalesce(NEW.summary, '') || ' ' ||
        coalesce(array_to_string(NEW.decisions, ' '), '')
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_agenda_search_vector ON agenda_items;
CREATE TRIGGER trg_agenda_search_vector
    BEFORE INSERT OR UPDATE ON agenda_items
    FOR EACH ROW EXECUTE FUNCTION update_agenda_search_vector();
