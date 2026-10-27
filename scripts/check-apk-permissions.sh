#!/usr/bin/env bash
set -euo pipefail
aapt="$1"
apk="$2"
permissions="$("$aapt" dump permissions "$apk")"
for permission in READ_PHONE_STATE READ_EXTERNAL_STORAGE WRITE_EXTERNAL_STORAGE READ_SMS RECEIVE_SMS; do
  if grep -Eq "^[[:space:]]*uses-permission[^:]*: name='android[.]permission[.]${permission}'" <<< "$permissions"; then
    echo "::error::Unexpected legacy permission android.permission.$permission in $apk"
    exit 1
  fi
done
manifest="$("$aapt" dump xmltree "$apk" AndroidManifest.xml)"
for declaration in android.permission.BIND_ACCESSIBILITY_SERVICE \
    android.accessibilityservice.AccessibilityService \
    android.permission.BIND_NOTIFICATION_LISTENER_SERVICE \
    android.service.notification.NotificationListenerService; do
  if grep -Fq "\"$declaration\"" <<< "$manifest"; then
    echo "::error::Unexpected global-access service $declaration in $apk"
    exit 1
  fi
done
echo "No unused phone/storage permissions or global-access services in $apk"
