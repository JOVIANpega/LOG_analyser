
import os
import sys
import tkinter as tk
from unittest.mock import MagicMock

# Add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import pandas as pd
from app.csv_processor import CSVProcessor

def verify_processing():
    # Mock the main app
    mock_app = MagicMock()
    mock_app.root = tk.Tk()
    
    processor = CSVProcessor(mock_app)
    
    # Set the analysis directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processor.analysis_dir = os.path.join(current_dir, "app", "Analysis_CSV_FILE")
    if not os.path.exists(processor.analysis_dir):
        os.makedirs(processor.analysis_dir)
        
    csv_file = os.path.join(current_dir, "MINE", "VALO360_AOCI_4Cam_Stitching_test1_log.csv")
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    print(f"Verifying CSV: {csv_file}")
    
    try:
        # Mock create_progress_window as well because it's called in copy_and_process_files
        mock_progress = MagicMock()
        processor.create_progress_window = MagicMock(return_value=mock_progress)
        
        # We also need to mock messagebox to avoid blocking
        import tkinter.messagebox
        tkinter.messagebox.askyesno = MagicMock(return_value=False)
        tkinter.messagebox.showinfo = MagicMock()
        tkinter.messagebox.showerror = MagicMock(side_effect=lambda title, msg: print(f"ERROR DIALOG: {msg}"))
        
        # Call the processing logic directly inside process_csv_file
        # Note: process_csv_file catches its own exceptions and shows a dialog
        processor.process_csv_file(csv_file)
        print("Verification script finished.")
    except Exception as e:
        print(f"VERIFICATION FAILED with unexpected exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_processing()
