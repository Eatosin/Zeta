#!/bin/bash
echo " Deploying to Production Container..."
docker build -t testforge-ai .
docker run -p 8000:8000 -p 8501:8501 --env-file .env testforge-ai
