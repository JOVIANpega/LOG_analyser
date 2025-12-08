# Implementation Plan - Phase Tracking and Highlighting

The user wants to track the execution phases (e.g., "Execute Phase 1 test") to see where the test failed. These lines should also be highlighted in dark green in the full log view.

## Proposed Changes

### `log_analyzer_gui.py`

#### `get_log_errors` method
- Scan the log content for lines matching the pattern `Execute Phase \d+` (case-insensitive).
- Store the list of found phases (line content and line number) in the result dictionary.
- Determine the "Last Executed Phase" to display.

#### `display_log_result` method
- Add a section to display the "Test Progress" or "Last Executed Phase".
- If errors are found, showing the last phase helps identify *when* it failed.
- Display format: "📋 測試進度: Phase 1 -> Phase 2 ..." or just the last one.

#### `show_full_log` method
- Add a new tag configuration for "phase_tag" with foreground color "dark green" (e.g., `#006400`).
- Apply this tag to all occurrences of the phase pattern.

## Verification Plan

### Manual Verification
- Run the application.
- Load a log file (if available) or create a dummy log with "Execute Phase X" lines.
- Verify that the summary shows the phases.
- Open the full log and verify the lines are green.
