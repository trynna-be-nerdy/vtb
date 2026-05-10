# Task 8: Pipeline publisher: DB write, Redis cache invalidation, and WebSocket broadcast

**Status:** pending
**Priority:** high
**Dependencies:** 2, 6

## Description
Implement and test the publisher that atomically writes validated agenda items to PostgreSQL, invalidates Redis cache keys, and broadcasts WebSocket notifications.

## Implementation Details
1. Locate `backend/pipeline/publisher.py` — verify `write_agenda_item()`, `update_meeting_overview()`, `invalidate_and_broadcast()`
2. Test DB write with a mock agenda item:
   ```python
   from sqlalchemy.orm import Session
   from app.database import engine
   from pipeline.publisher import write_agenda_item

   with Session(engine) as db:
       item = write_agenda_item(
           db, meeting_id=test_meeting_id, item_order=0,
           prompt1={'title': 'Test Item', 'summary': 'Test summary ' * 10,
                    'decisions': [], 'action_items': [], 'key_figures': {}},
           prompt2={'primary_category': 'general', 'secondary_tags': [],
                    'urgency': 'routine', 'fiscal_impact': False, 'affects_schools': []},
           source_pdf_url='https://example.com/test.pdf',
           raw_chunk='raw text here'
       )
       db.commit()
       print('Written item ID:', item.id)
   ```
3. Verify the `search_vector` field is automatically populated by the trigger after INSERT
4. Test Redis invalidation patterns: 'meetings:list:*', 'meetings:detail:{id}', 'categories:{slug}:*'
5. Test WebSocket broadcast publishes to the `lcps:new_content` channel
6. Verify `update_meeting_overview()` sets processing_status = 'completed'

## Test Strategy
AgendaItem inserted with correct fields. search_vector is not NULL after INSERT. Redis keys matching invalidation patterns are deleted. WebSocket channel receives broadcast message.
