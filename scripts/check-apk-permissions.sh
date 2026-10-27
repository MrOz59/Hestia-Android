#!/usr/bin/env bash
set -euo pipefail
aapt="$1"
apk="$2"
permissions="$("$aapt" dump permissions "$apk")"
for permission in READ_PHONE_STATE READ_EXTERNAL_STORAGE WRITE_EXTERNAL_STORAGE; do
  if grep -Eq "^[[:space:]]*uses-permission[^:]*: name='android[.]permission[.]${permission}'" <<< "$permissions"; then
    echo "::error::Unexpected legacy permission android.permission.$permission in $apk"
    exit 1
  fi
done
echo "No unused phone/storage permissions in $apk"
