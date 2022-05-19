#!/bin/sh

python3 generate_build_data_from_gradle_logs.py

python3 auto_jacoco_gradle.py
