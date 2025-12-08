# Implementation Plan - Search Defaults and Multi-Log Prioritization

The user wants to improve the search experience in the full log view and ensure that logs with "doesn't match" errors are prioritized in the main display when analyzing multiple files.

## Proposed Changes

### `log_analyzer_gui.py`

#### `show_full_log` method
- Set `search_var` default value to `"doesn't match"`.
- Bind `<Return>` key on `search_entry` to trigger `search_log`.

#### `analyze_logs` method
- Refactor to separate analysis from display.
- **Step 1**: Iterate through `log_data` and call a modified `analyze_single_log` (or a new helper) to get error data *without* printing to the text widget immediately.
    - *Wait*, `analyze_single_log` currently prints to `self.result_text`. I should modify it to return the result data structure instead of printing, OR split it into `get_log_errors` and `display_log_errors`.
    - **Refactoring Strategy**:
        - Rename `analyze_single_log` to `process_log_errors` (returns error list and status).
        - Create `display_log_result` (takes error list and prints to GUI).
- **Step 2**: Collect all results.
- **Step 3**: Sort results.
    - Priority 1: Logs with "doesn't match" errors.
    - Priority 2: Logs with other errors.
    - Priority 3: Passed logs.
- **Step 4**: Iterate through sorted results and call `display_log_result`.

#### `analyze_single_log` (Refactor)
- Split into `analyze_log_content` (returns errors) and `display_analysis_result` (updates UI).
- `analyze_log_content` will contain the logic for finding "doesn't match", "ERROR", extracting context, and filtering.
- `display_analysis_result` will contain the logic for inserting text into `result_text`, creating "View Full Log" buttons, etc.

## Verification Plan

### Manual Verification
- **Search**: Open a full log, verify "doesn't match" is pre-filled. Press Enter, verify it searches.
- **Priority**: Load multiple logs (some with "doesn't match", some with "ERROR", some PASS). Verify that logs with "doesn't match" appear at the top of the list in the main window.
