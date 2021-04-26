#!/bin/bash

tmux kill-session -t CoraBot
tmux new -t CoraBot
python3 main.py
