#!/bin/bash
docker build -t hrsync:latest --build-arg NOCACHE=$(date +%s) .
