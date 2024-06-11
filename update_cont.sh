#!/bin/bash
git pull
docker build -t pharm .
docker run --rm --restart unless-stopped pharm
