# Task 6: Pipeline validator: implement and verify all 10 quality checks

**Status:** pending
**Priority:** high
**Dependencies:** 3

## Description
Ensure the validation gate correctly accepts good Gemma 4 output and rejects bad output before any database write.

## Implementation Details
1. Locate `backend/pipeline/validator.py` — verify `validate_item(prompt1, prompt2)` raises `ValidationError` with descriptive messages
2. Verify all 10 checks are implemented:
   - Check 1: title is non-empty string
   - Check 2: title ≤ 300 chars
   - Check 3: summary is non-empty string
   - Check 4: summary ≥ 80 chars
   - Check 5: summary not in placeholder set (n/a, none, unknown, tbd)
   - Check 6: decisions is a list, ≤ 20 items
   - Check 7: action_items is a list
   - Check 8: primary_category is one of the 12 valid slugs
   - Check 9: urgency is 'routine', 'notable', or 'significant'
   - Check 10: fiscal_impact is a boolean
3. Write unit tests:
   ```python
   from pipeline.validator import validate_item, ValidationError
   import pytest

   # Should pass
   validate_item(
     {'title': 'Budget Amendment', 'summary': 'The board approved a $2M budget amendment for new buses.' * 2,
      'decisions': ['Approved 5-2'], 'action_items': []},
     {'primary_category': 'budget-finance', 'urgency': 'notable', 'fiscal_impact': True}
   )

   # Should fail — short summary
   with pytest.raises(ValidationError, match='Check 4'):
     validate_item({'title': 'X', 'summary': 'Too short'}, {...})
   ```
4. Run all validator unit tests

## Test Strategy
All 10 failure cases raise ValidationError with the correct check number. A valid Gemma 4 output passes without error. Tests run in < 1 second (no Ollama calls).
