#!/usr/bin/env bash

set -euo pipefail
"$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/helpers/install.sh" "$HOME/.config/opencode/skills"
