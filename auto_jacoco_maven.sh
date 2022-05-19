#!/bin/sh

python3 generate_build_data_from_maven_logs.py

python3 auto_jacoco_maven.py
