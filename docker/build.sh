#!/bin/bash

LOCAL_USER_UID=$(id -u) LOCAL_USER_GID=$(id -g) docker compose build
