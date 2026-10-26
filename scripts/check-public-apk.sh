#!/usr/bin/env bash
set -euo pipefail
apk="$1"
abi="$2"
certificate_file="$3"
build_tools="${ANDROID_HOME:?}/build-tools/36.0.0"
metadata="$("$build_tools/aapt" dump badging "$apk")"
if grep -Fq application-debuggable <<< "$metadata"; then
  echo "::error::Public APK must not be debuggable: $apk"
  exit 1
fi
signature="$("$build_tools/apksigner" verify --verbose --print-certs "$apk")"
grep -Fq 'Verified using v1 scheme (JAR signing): true' <<< "$signature"
grep -Fq 'Verified using v2 scheme (APK Signature Scheme v2): true' <<< "$signature"
certificate="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' <<< "$signature")"
[[ "$certificate" =~ ^[a-fA-F0-9]{64}$ ]]
if [[ -n "${HESTIA_EXPECTED_CERT_SHA256:-}" ]]; then
  [[ "$certificate" == "$HESTIA_EXPECTED_CERT_SHA256" ]] || {
    echo '::error::APK signer does not match the configured persistent key'
    exit 1
  }
fi
if [[ -f "$certificate_file" ]]; then
  [[ "$(cat "$certificate_file")" == "$certificate" ]] || {
    echo '::error::APKs have different signing certificates'
    exit 1
  }
else
  printf '%s\n' "$certificate" > "$certificate_file"
fi
entries="$(unzip -Z1 "$apk")"
if [[ "$abi" == arm64-v8a ]]; then
  grep -Fxq 'lib/arm64-v8a/libpyrowave-shared.so' <<< "$entries"
  core="$(mktemp)"
  trap 'rm -f "$core"' EXIT
  unzip -p "$apk" lib/arm64-v8a/libmoonlight-core.so > "$core"
  symbols="$("$ANDROID_HOME/ndk/27.0.12077973/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf" --wide --dyn-syms "$core")"
  grep -Fq PyroWaveBridge_nativeDecode <<< "$symbols"
else
  if grep -Fq 'libpyrowave-shared.so' <<< "$entries"; then
    echo "::error::Unexpected codec library for unsupported ABI: $abi"
    exit 1
  fi
fi
echo "Public APK signature, release flags and codec verified: $apk"
