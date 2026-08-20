#!/usr/bin/env bash
#
# Consistency checks between the release version and the schema version.
#
#   release version — VERSION file, git tags; full SemVer (e.g. 2.1.0)
#   schema version  — XSD file name, XSD header, version="…" in documents;
#                     bumps only on a breaking change (e.g. 2.0)
#
# The rule enforced here: MAJOR of the release version equals MAJOR of the
# schema version, and every shipped XML declares that schema version.
#
set -euo pipefail

cd "$(dirname "$0")/.."

fail() { echo "FAIL: $*" >&2; exit 1; }

[ -f VERSION ] || fail "VERSION file is missing"
RELEASE="$(tr -d '[:space:]' < VERSION)"
echo "$RELEASE" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' \
    || fail "VERSION '$RELEASE' is not MAJOR.MINOR.PATCH"

SCHEMA_FILE="$(ls sylius-import-*.xsd)"
[ "$(echo "$SCHEMA_FILE" | wc -l)" -eq 1 ] \
    || fail "expected exactly one sylius-import-*.xsd, found: $SCHEMA_FILE"

SCHEMA_VER="$(echo "$SCHEMA_FILE" | sed -E 's/^sylius-import-(.+)\.xsd$/\1/')"
RELEASE_MAJOR="${RELEASE%%.*}"
SCHEMA_MAJOR="${SCHEMA_VER%%.*}"

[ "$RELEASE_MAJOR" = "$SCHEMA_MAJOR" ] \
    || fail "release MAJOR ($RELEASE_MAJOR) != schema MAJOR ($SCHEMA_MAJOR).
       A breaking schema change needs a new XSD file AND a MAJOR release."

grep -q "version $SCHEMA_VER" "$SCHEMA_FILE" \
    || fail "XSD header does not mention 'version $SCHEMA_VER'"

# Every shipped document must declare the current schema version.
BAD=0
for f in examples/*.xml tests/*.xml; do
    # Read the version attribute off the root element only, never off the
    # <?xml version="1.0"?> declaration.
    DECLARED="$(grep -m1 '<sylius-import' "$f" \
                 | grep -o ' version="[^"]*"' \
                 | sed 's/ version="\(.*\)"/\1/')"
    if [ "$DECLARED" != "$SCHEMA_VER" ]; then
        echo "  $f declares version=\"$DECLARED\", expected \"$SCHEMA_VER\"" >&2
        BAD=1
    fi
done
[ "$BAD" -eq 0 ] || fail "some documents declare the wrong schema version"

# CHANGELOG must carry an entry for the release in VERSION.
grep -q "^## \[$RELEASE\]" CHANGELOG.md \
    || fail "CHANGELOG.md has no '## [$RELEASE]' section"

echo "OK  release $RELEASE / schema $SCHEMA_VER / $SCHEMA_FILE"
