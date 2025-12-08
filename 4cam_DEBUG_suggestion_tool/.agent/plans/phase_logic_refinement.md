# Implementation Plan - Phase Logic Refinement

The user wants to refine the phase display logic:
1.  **Ignore Reset Phases**: Phases >= 90 (e.g., Phase 97) should be ignored when determining the "failed phase". The last phase < 90 should be the one highlighted in red.
2.  **Show Last Command**: For the identified "failed phase", display the last command executed within that phase, as this is likely the cause of the failure.

## Proposed Changes

### `log_analyzer_gui.py`

#### `get_log_errors` method
- Update phase extraction to capture the phase number and start position.
- Store phases as a list of dictionaries: `{'name': str, 'number': int, 'start_pos': int, 'end_pos': int}`.
- Identify the **Last Valid Phase** (last phase with number < 90).
- For this Last Valid Phase, search the content between its start and the start of the next phase (or end of file).
- Extract the **last command** found in this region using existing command patterns.
- Return the phases list (updated with command info) and the index of the phase to highlight.

#### `display_log_result` method
- Update the loop for displaying phases.
- Use the calculated "highlight index" to determine which phase gets the `phase_error_red` tag.
- If the highlighted phase has a "last command" associated with it, display it below the phase line.
    - Format: `      └── 最後指令: [Command]` (Indented)

## Verification Plan

### Manual Verification
- **Phase Logic**:
    - Create/Use a log with `Execute Phase 6` ... `Execute Phase 97`.
    - Verify Phase 6 is Red, Phase 97 is normal.
- **Command Display**:
    - Verify that under Phase 6, the last command (e.g., `(LAN) > ...`) is displayed.
