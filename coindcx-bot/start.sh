#!/bin/bash
export PYTHONPATH=/app:$PYTHONPATH
cd /app
streamlit run src/dashboard/app.py --server.port=8501 --server.address=0.0.0.0 &
python -m src.main --api