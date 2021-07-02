#!/usr/bin/env bash

# clean up previous builds
docker rm wikispeech-server-sox-proxy
docker rmi --force wikispeech-server-sox-proxy

docker rm wikispeech-server-sox-proxy-test
docker rmi --force wikispeech-server-sox-proxy-test

# build docker
blubber .pipeline/blubber.yaml test | docker build --tag wikispeech-server-sox-proxy-test --file - .
blubber .pipeline/blubber.yaml production | docker build --tag wikispeech-server-sox-proxy --file - .
