#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist/server dist/.openai/drizzle
cp worker/index.js dist/server/index.js
cp .openai/hosting.json dist/.openai/hosting.json
cp -r drizzle/. dist/.openai/drizzle/
