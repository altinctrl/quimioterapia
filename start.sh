#!/bin/bash
killall uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 2> server.log &
