# Hestia Android integration plan

Hestia Android is a fork of [Artemis](https://github.com/ClassicOldSong/moonlight-android), based on Moonlight Android. The goal is to add opt-in Hermes/Hestia protocol extensions while preserving the existing GameStream streaming path and compatibility with non-Hermes hosts.

This document describes **planned work**, not features implemented in this fork.

## Design constraints

- Keep video, audio, controller, pointer, and pairing transport unchanged in the first integration.
- Never require Hestia extensions for basic GameStream streaming.
- Discover extensions per host with `GET /api/hestia/v1/capabilities`; treat missing, malformed, incompatible, or unsuccessful responses as a normal legacy-host outcome.
- Hestia v1 is an HTTP API extension, **not** a replacement for the Moonlight/GameStream transport.
- All privileged Hestia endpoints must use the existing paired-client TLS certificate, not the web UI admin password.
- Gate actions using advertised capabilities and permissions; do not assume all Hermes versions implement every feature.
- Preserve upstream notices, licenses, and provenance. Keep Artemis-specific fixes mergeable until the fork is independently maintained.

## Current host API

Hermes documents these endpoints in [docs/api.md](https://github.com/MrOz59/Hermes/blob/main/docs/api.md):

| Endpoint | Intended Android behavior |
| --- | --- |
| `GET /api/hestia/v1/capabilities` | Discover supported protocol versions, features, and streaming limits before offering host-specific controls |
| `GET /api/hestia/v1/client/permissions` | Show/enable only actions granted to the paired client |
| `POST /api/hestia/v1/session/prepare` | Submit supported virtual-display, size, refresh-rate, and other session hints before ordinary GameStream launch |
| `POST /api/hestia/v1/session/stop` | Stop only the calling client's session |
| `GET /api/hestia/v1/display/status` | Inspect virtual/physical display state |
| `POST /api/hestia/v1/display/recover` | Explicit user-initiated display recovery when permitted |
| `GET /api/hestia/v1/diagnostics` | Display readiness and runtime diagnostics |
| `GET/POST /api/hestia/v1/clipboard` | Opt-in clipboard synchronization with permission checks |
| `GET /api/hestia/v1/commands` | List host-approved commands |
| `POST /api/hestia/v1/commands/run` | Execute only a selected, authorized server command |

The capabilities response advertises `hestia_protocol`, `min_client_protocol`, and `max_client_protocol`. For now, Android should only activate extensions when **v1** is inside the server-supported range and the response is valid. Do not assume a future protocol revision is backwards-compatible.

## Implementation sequence

1. **Baseline build**: establish an Android CI build on the fork's actual Gradle flavors and document upstream sync. Do not change package IDs in the same PR.
2. **Discovery**: add a small, separately testable Hestia API/client layer and a host capability cache with explicit legacy fallback. Test invalid JSON, HTTP errors, timeouts, unsupported versions, and multiple hosts.
3. **Authentication**: reuse the paired client's certificate/key from the existing host connection in the Hestia API HTTPS client; never silently downgrade privileged calls to insecure HTTP.
4. **Session control**: implement prepare-before-launch and failure-safe fallback; avoid invoking `stop` on sessions owned by another client. Add feature-gated UI for VD, display status, recovery, and diagnostics.
5. **Additional controls**: clipboard and approved server commands, gated by per-client permissions and explicit user actions.
6. **Input quality**: audit Android stylus events through `Game.handleMotionEvent` → `sendPenEvent` → Hermes → libvirtualhid. Preserve pressure, hover, tool/eraser, tilt and button semantics; add synthetic input tests, especially stylus + touch combinations.
7. **Branding and distribution**: update app labels/icons/package IDs, signing and release workflow in a separate reviewed PR; verify side-by-side installation and upgrade behavior before shipping.

## Stylus considerations

Artemis currently distinguishes stylus/eraser tool types and sends pen events with pressure, contact geometry, rotation, tilt and stylus buttons. However, its pointer capture and mouse fallback paths require auditing. A successful Android-side event does not prove Linux applications see a tablet: Hermes must handle the pen protocol and libvirtualhid must expose a coherent uinput tablet device.

No hardware validation is claimed. Synthetic tests cover event mapping, not Samsung-specific firmware or compositor behavior.

## Acceptance criteria for the first functional milestone

- Existing pairing, application listing and GameStream launch still work against non-Hermes hosts.
- Hermes v1 capabilities are parsed and version-checked without crashing or blocking normal streaming.
- A paired Android client successfully calls a permission-protected API with its own certificate.
- When an extension is unavailable or fails, normal streaming remains usable and the failure is visible in diagnostics.
- CI builds the supported Android flavors; no experimental functionality is advertised as production-ready before testing.
