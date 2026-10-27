# Pairing reliability

Some testers reported needing three or four pairing attempts. Without logs from
the affected host/device, that report alone does not identify the failing phase.
RC3 addresses concrete failure paths found during code review:

- An I/O error or malformed reply could leave the host's partially completed
  pairing session behind. Every unsuccessful attempt now sends a best-effort
  cancellation. A cancellation failure preserves the original error.
- Repeated taps could create overlapping handshakes sharing the same client
  identity and PIN dialog. Pairing is now limited to one active UI operation,
  including across activity recreation, and lifecycle/menu callbacks do not
  restart host polling during it. The initial PIN wait has a three-minute total
  timeout, so abandoning a PIN dialog cannot block pairing indefinitely.
- Pairing commands use GET but change server state. Automatic connection retries
  and redirects are disabled for those commands, so a lost response does not
  silently replay a challenge or resend pairing material elsewhere.
- The final HTTPS confirmation can be repeated safely after a transient network
  error or a brief authorization delay. It has three attempts with 250/500 ms
  backoff. Challenge commands and the PIN exchange are never automatically
  restarted. Certificate/hostname validation failures, malformed replies and an
  explicit pairing rejection remain failures.

## Android NSD crash when opening pairing (after RC3)

A device crash report identified `RejectedExecutionException` in Android's
`NsdManager.ServiceHandler`: the framework dispatched a service-info callback
onto an already terminated worker. On Android 14+, pausing discovery for pairing
closes the native agent through `FallbackDiscoveryAgent`. Unregistration is
asynchronous, so the framework can still dispatch an update or its unregistration
notification after the worker shuts down. Both universal and ABI-specific RC3
APKs use this same code and are affected.

The fix passes Android a lifecycle-aware executor that serializes submissions
with close and drops dispatches arriving after close. The actual worker still
shuts down. Queued callbacks and delayed discovery/registration callbacks also
check session identity, so stopped agents cannot publish hosts or trigger a
fallback in a resumed session. Late discovery-start cleanup is best-effort.

Regression tests run on Android 14/API 34 and Android 16/API 36. They submit
framework callbacks after confirmed worker termination, race close against
submission, delay queued callbacks and exercise a real native agent inside the
fallback wrapper across pairing-style pause/resume. This fixes the reported
client crash independently of the companion Hermes update below. Physical-device
retesting remains necessary.

## Companion Hermes update

Hermes also had stale-session and lifetime defects: a repeated request could
reuse the old phase, its HTTP `/unpair` endpoint was missing, and successful
pairing could access a session after erasing its map entry. Web UI PIN submission
could also target an entry no longer waiting for a PIN. The companion fix is
[Hermes PR #77](https://github.com/MrOz59/Hermes/pull/77). Full recovery from stale
Hermes sessions requires that host update; the existing Hermes RC3 release tag
is unchanged. The Android changes remain compatible with existing hosts.

PIN verification, server-secret signature verification, pinned server
certificates and TLS validation are retained. The log identifies handshake
phases without logging PINs, OTP passphrases, request URLs or certificate/secret
payloads. Debug HTTP logging also excludes pairing requests and responses.

## Validation and reports

Tests use a host peer that computes AES challenges and RSA signatures and checks
the client's proof. They cover successful PIN/OTP pairing, incorrect PINs,
tampered secrets, missing fields, network interruption, cleanup failures,
bounded HTTPS retries and certificate/hostname failures. Local HTTP-server tests
cover lost replies and redirects; UI tests cover overlapping attempts and
polling suppression. These tests do not substitute for physical-device testing
on the reporter's network.

For a continuing failure, include the exact Hestia and host versions, Android
version/device model, PIN or OTP method, connection type (LAN/VPN), the visible
error and client/host logs around that attempt. Never include the PIN, passphrase
or private keys. Note the last `Pairing phase:` line and whether the host already
lists the device as paired. Retest pairing after removing only that test client
from the host, then confirm app-list access and a stream/reconnect.
