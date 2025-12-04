#!/bin/bash

# Start MongoDB via Docker
echo "Starting MongoDB..."
docker run -d -p 27017:27017 --name fintrack-mongo mongo:latest 2>/dev/null || \
docker start fintrack-mongo 2>/dev/null || \
echo "Warning: Could not start MongoDB. Please ensure Docker is running or install MongoDB manually."

sleep 2
echo ""

