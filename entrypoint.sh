#!/bin/bash
nohup python -m flask run --host=0.0.0.0 --no-debug &
nohup streamlit run streamlit_app.py --server.fileWatcherType=none &