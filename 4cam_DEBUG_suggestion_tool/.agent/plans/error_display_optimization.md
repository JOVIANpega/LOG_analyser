# Implementation Plan - Error Display Optimization

The user wants to optimize how errors and phases are displayed to reduce noise and focus on the most critical information.

## Proposed Changes

### `log_analyzer_gui.py`

#### `update_font_size` method
- Add a new tag configuration `phase_error_red` for displaying the failed phase in red.

#### `display_log_result` method
- Modify the phase display loop.
- If the log is not a PASS (or has errors), apply the `phase_error_red` tag to the **last** phase in the list.
- Keep other phases as `reason_text`.

#### `show_full_log` method
- Implement error filtering logic before displaying the summary and highlighting lines.
- **Filtering Logic**:
    1. Filter for `doesn't match` errors.
    2. If found, use ONLY these errors.
    3. If NOT found, use ONLY the **last** error from the original list (assuming it's the fatal one).
- Use this filtered list for:
    - The "Error Summary" section (clickable links).
    - The red line highlighting in the log text.

## Verification Plan

### Manual Verification
- **Phase Highlighting**:
    - Analyze a log with errors.
    - Verify that in the main window, the list of phases shows the last one in Red.
- **Full Log Error Filtering**:
    - Open a log with multiple "doesn't match" errors. Verify only those are listed/highlighted.
    - Open a log with multiple generic errors (no "doesn't match"). Verify only the *last* one is listed/highlighted.
