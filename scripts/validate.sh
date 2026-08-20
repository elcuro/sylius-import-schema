#!/usr/bin/env bash
#
# Validate every example and test XML file against the XSD.
#
# Uses xmllint when it is already available (CI runners), otherwise falls
# back to a disposable container so nothing has to be installed on a
# developer machine.
#
set -euo pipefail

cd "$(dirname "$0")/.."

SCHEMA="$(ls sylius-import-*.xsd | head -n1)"

run_xmllint() {
    local failed=0
    for f in examples/*.xml tests/*.xml; do
        printf '%-32s ' "$f"
        if xmllint --schema "$SCHEMA" "$f" --noout 2>&1; then
            :
        else
            failed=1
        fi
    done
    return $failed
}

if command -v xmllint >/dev/null 2>&1; then
    run_xmllint
elif command -v docker >/dev/null 2>&1; then
    docker run --rm -v "$PWD":/work -w /work alpine:latest sh -c \
        "apk add --no-cache libxml2-utils >/dev/null 2>&1 && \
         for f in examples/*.xml tests/*.xml; do \
             printf '%-32s ' \"\$f\"; \
             xmllint --schema $SCHEMA \"\$f\" --noout; \
         done"
else
    echo "Neither xmllint nor docker is available." >&2
    exit 1
fi
