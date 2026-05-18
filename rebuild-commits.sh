#!/bin/sh

./generate.py all --stage vanilla
git add -A
git commit -m "Import vanilla WireGuard packages"

./generate.py all --stage files
git add -A
git commit -m "Rename WireGuard package files to AmneziaWG"

./generate.py all --stage text
git add -A
git commit -m "Rename WireGuard identifiers to AmneziaWG"

./generate.py all --stage full
git add -A
git commit -m "Add AmneziaWG-specific changes"
