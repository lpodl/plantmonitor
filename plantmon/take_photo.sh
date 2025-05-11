#!/bin/bash
# load env
SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "${SCRIPT_DIR}/../.env"
# create dir if it doesn't exist
mkdir -p "${PIC_PATH}"

fswebcam --banner-colour "#40916C" --line-colour "#D8F3DC" -r 1920x1080 --no-shadow --png 0 "${PIC_PATH}/$(date +"%Y-%m-%d_%H%M").png"
