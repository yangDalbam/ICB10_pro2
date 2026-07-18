import sys
import os
import pandas as pd

# Mock streamlit so we can import app.py without executing widgets
class MockSt:
    def cache_data(self, func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func
    def cache_resource(self, func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func
    def __getattr__(self, name):
        from unittest.mock import MagicMock
        return MagicMock()

sys.modules['streamlit'] = MockSt()

# Import app2
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, "..", "korea-trip-data2")))

try:
    import app as app2
    df_merged = app2.get_integrated_data()
    
    # Save to CSV in korea-trip-data2/data
    out_dir = os.path.abspath(os.path.join(current_dir, "..", "korea-trip-data2", "data"))
    os.makedirs(out_dir, exist_ok=True)
    
    df_merged.rename(columns={"region": "지역", "interest_median": "관심도", "visit_median": "방문도"}, inplace=True)
    
    out_path = os.path.join(out_dir, "aggregated_dashboard_data.csv")
    df_merged.to_csv(out_path, index=False)
    print(f"Data successfully exported to {out_path}")
except Exception as e:
    import traceback
    traceback.print_exc()
