#!/usr/bin/env bash
# Verify that the shipped phone APK is also discoverable by TV launchers.
set -euo pipefail
aapt_bin="$1"
apk="$2"
badging="$("$aapt_bin" dump badging "$apk")"
for expected in \
  "leanback-launchable-activity: name='com.limelight.PcView'" \
  "uses-feature-not-required: name='android.hardware.touchscreen'" \
  "uses-feature-not-required: name='android.software.leanback'"; do
  if ! grep -Fq "$expected" <<< "$badging"; then
    echo "::error::Missing shared phone/TV APK metadata: $expected ($apk)"
    exit 1
  fi
done
manifest="$("$aapt_bin" dump xmltree "$apk" AndroidManifest.xml)"
if ! grep -Eq 'android:banner\(.*\)=@0x' <<< "$manifest"; then
  echo "::error::Missing TV launcher banner: $apk"
  exit 1
fi
echo "Phone/TV launcher metadata verified: $apk"
