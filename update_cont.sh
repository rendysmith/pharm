#!/bin/bash
git pull
docker build -t pharm .
docker run --restart unless-stopped pharm
