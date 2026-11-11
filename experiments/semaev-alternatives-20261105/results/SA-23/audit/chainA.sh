#!/bin/bash
cd /home/user/semaev-runs/SA-23
python3 audit/lift2.py 37 12 600 3
python3 audit/lift2.py 17 18 10800 1 work/s_17_18.txt
python3 audit/lift2.py 23 24 18000 1
python3 audit/lift2.py 29 30 18000 1
