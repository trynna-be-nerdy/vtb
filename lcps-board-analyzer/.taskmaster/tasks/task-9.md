# Task 9: Pipeline worker: wire APScheduler to run the full end-to-end pipeline

**Status:** pending
**Priority:** high
**Dependencies:** 3, 4, 5, 6, 7, 8

## Description
Run the complete automated pipeline on a real LCPS document — from URL discovery through Gemma 4 analysis to live content in the database.

## Implementation Details
1. Locate `backend/pipeline/worker.py` — verify `run_pipeline()` and `_execute_pipeline()` flow
2. Set `PIPELINE_INTERVAL_HOURS=999` in .env temporarily to prevent auto-scheduling
3. Run a single manual pipeline pass:
   ```bash
   cd backend && python -c "from pipeline.worker import run_pipeline; run_pipeline()"
   ```
4. Watch the logs — verify each step runs: discover → deduplicate → download → extract → chunk → Gemma 4 → validate → write → publish
5. After run, verify in DB:
   ```sql
   SELECT COUNT(*) FROM meetings;        -- should be ≥ 1
   SELECT COUNT(*) FROM agenda_items;    -- should be ≥ 1
   SELECT title, primary_category, urgency FROM agenda_items LIMIT 5;
   SELECT status FROM pipeline_runs ORDER BY started_at DESC LIMIT 1;  -- 'completed'
   ```
6. Run a second time — verify deduplication skips already-processed documents (documents_new stays 0)
7. Test that failed Gemma 4 items increment items_failed in pipeline_run and do NOT appear in agenda_items
8. Restore normal PIPELINE_INTERVAL_HOURS after verification
9. Test APScheduler: start worker.py, verify it logs 'Pipeline run starting' on schedule

## Test Strategy
After one manual run: ≥1 meeting and ≥1 agenda_item in DB. pipeline_runs shows status='completed'. Second run produces documents_new=0. All agenda_items have valid primary_category and non-null summary.
