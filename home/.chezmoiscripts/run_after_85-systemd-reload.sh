#!/bin/sh
# Pick up changed user units after every apply; enablement lives in 90-session.
set -eu
if command -v systemctl >/dev/null && [ -n "${XDG_RUNTIME_DIR:-}" ]; then
    systemctl --user daemon-reload
fi
