#!/usr/bin/env bash

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

rm -rf "$SCRIPT_DIR/../Old"
rm -rf "$SCRIPT_DIR/../Paradigms"
rm -rf "$SCRIPT_DIR/../Philosophy"
rm -rf "$SCRIPT_DIR/../Programming"
rm -rf "$SCRIPT_DIR/../Math"
rm -rf "$SCRIPT_DIR/../assets"
rm -f "$SCRIPT_DIR/../index.html"
rm -f "$SCRIPT_DIR/../cv.html"
rm -f "$SCRIPT_DIR/org/index.org"