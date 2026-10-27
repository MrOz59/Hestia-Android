# Play Protect investigation — 27 October 2026

Issue: [#16](https://github.com/MrOz59/Hestia-Android/issues/16).

This investigation compares downloaded release APKs, not only source manifests.
It identifies excess permissions in Hestia RC2; it does **not** establish the
reason for Google's classification or demonstrate that a new build is accepted.
The warning category is now known from the user's screenshot (see below).
A real-device retest of a new build remains necessary.

## Published APK comparison

| Property | Moonlight v12.2 | Artemis v20.2.6 | Hestia October RC2 |
| --- | --- | --- | --- |
| Package | `com.limelight` | `com.limelight.noir` | `com.mroz59.hestia.nightly` |
| Embedded version | `12.2` | `20.2.6` | `20.2.6-nightly.51` |
| Target SDK | 36 | 34 | 34 |
| Debuggable / testOnly | false / false | false / false | false / false |
| Signature schemes present | v1, v2 | v1, v2 | v1, v2 |
| Certificate validity starts | 15 March 2014 | 10 July 2024 | 27 October 2026 |
| Keyboard accessibility service | absent | present | present |
| `READ_PHONE_STATE` | absent | absent | **present** |
| `READ_EXTERNAL_STORAGE` | absent | absent | **present** |
| `WRITE_EXTERNAL_STORAGE` | absent | absent | **present** |
| `RECORD_AUDIO` | absent | absent | present, for opt-in microphone forwarding |

The three phone/storage permissions are absent from Hestia's source manifests
but present in its final merged APK manifest. Dependencies can introduce
permissions, including compatibility permissions when their target SDK is old.
The manifest merger report should be used to identify the exact dependency;
the APK comparison alone cannot identify it.

Hestia's application code does not request these runtime permissions or use
APIs requiring phone-state permission. Profile files are app-private;
user-selected document imports/exports use the Storage Access Framework.
Explicit manifest removal rules now exclude these three permissions. CI checks
both the merged manifest and every packaged APK so dependency updates cannot
silently reintroduce them. Nightly artifacts also retain manifest merger reports.

Artemis and Hestia both declare keyboard accessibility with window-content
retrieval and interactive-window flags; their implementation forwards keys only
while streaming. This is shared inherited behavior, not a difference explaining
why one APK is accepted on a particular device. The first permission cleanup retained this service while awaiting the exact
warning. The subsequent change below removes it entirely.

All three certificates are self-signed and all three APKs have v1/v2 signature
blocks. Hestia's RC2 certificate is permanent but newly created. An unknown-app
classification is possible; certificate age alone does not prove reputation or
explain a malware verdict. Do not rotate the signing key, copy another app's
package identity, or disable Play Protect as a fix.

## Confirmed warning category and focused keyboard capture

The user supplied a screenshot with the heading "O app foi bloqueado para
proteger seu dispositivo" and text stating that the app can request sensitive
data and increase the risk of identity theft or financial fraud. This matches
Google's **App blocked to protect your device** guidance for internet-sideloaded
apps declaring high-risk permissions, including accessibility. It is a different
prompt from the harmful-app or unknown-app scan prompts. The screenshot identifies
Hestia Nightly but does not show its embedded build number.

Neither RC2 nor nightly.53 declares SMS reception/reading or a notification-listener
service. Both still declare the inherited keyboard accessibility service. This
makes accessibility the relevant declared capability for this documented warning;
the screenshot alone is not a complete malware assessment or a server-side verdict.

The new build removes the accessibility service, its implementation, its XML
configuration and its unused descriptions from every flavor. No disabled or
alternate accessibility service remains in the APK. CI now checks the **packaged**
manifest for accessibility/notification-listener declarations and SMS permissions,
in addition to checking for the unused phone/storage permissions.

Keyboard shortcuts now use Android's public window-scoped
`WindowManager.LayoutParams.setKeyboardCaptureEnabled` when that API is available
(Android 16.1 / API 36.1 and later). `CAPTURE_KEYBOARD` is a **normal** permission;
Android delivers keys only to the focused app, retains reserved system actions,
and allows users to escape capture. The method is resolved reflectively as a
forward-compatible public API so Hestia can continue compiling against API 36.
The existing input-grab toggle enables/disables this capture. Android 16.0 and
older versions safely retain the existing Samsung-specific fallback where
supported, plus ordinary keyboard, touch, mouse, controller and TV-remote input.

Tradeoff: on older/non-supporting Android devices, shortcuts intercepted by the
OS can no longer be forwarded using a global accessibility service. This is a
real capability removal, not a renamed service or a request to disable device
protection. The app no longer needs users to enable accessibility access.

The new APK keeps Hestia's identity and permanent signing key, and receives a
higher Nightly version code. The published RC2 and nightly.53 remain unchanged.
A successful build proves the restricted declarations are absent; acceptance by
Play Protect must still be confirmed on the affected device.

## Evidence for the unchanged RC2 APK

File: `Hestia-Android-nightly-arm64-v8a.apk`

- APK SHA-256: `6a2730424fbd36a9051c8f3a89e7e003ce98616e08d66f9d60ccbe2d2745344a`
- Certificate SHA-256: `3f80a384597e446daf48c32497e4008e1bbbac4c5e5cc1d843b0c5b37d2ee26e`
- Source: `39a4ab5bd7f12fb0ac6aa224121b004156032d10`
- Build: [40431548596](https://github.com/MrOz59/Hestia-Android/actions/runs/40431548596)

Comparator APK hashes:

- Artemis `artemis-nonRoot_game-release.apk` v20.2.6:
  `6735b5fdd790410ea726754235f49757fa594ef01da1e5acadf72690c9423f6c`
- Moonlight `app-nonRoot-release.apk` v12.2:
  `a871f6190365386ef3ac5722a016d4da015ee1555631ec257f6e5dc3f4a45fe0`

The existing RC2 release remains immutable. Permission changes require a new
build with its own version and hash, signed by the same permanent key.

## Distinguish the warning before escalating

Record the full message or screenshot, APK filename and SHA-256, Android/device
model, install source, and whether the same device accepts the comparator APKs.
Do not treat these different prompts as the same problem:

- **Unknown app / scan recommended:** allow Google's security scan. The separate
  "Send App for Security Check" prompt is not removed by an appeal.
- **App blocked to protect your device / sensitive data:** Google's guidance
  identifies internet-sideloaded apps with accessibility and certain other
  sensitive permissions as affected in selected markets. Removing unused
  phone/storage permissions does not remove the accessibility declaration.
- **Harmful app:** investigate the named detection and dependencies. If the
  classification is incorrect, submit a Play Protect appeal for the exact APK.
- **Built for an older Android version:** evaluate target-SDK migration and its
  compatibility changes separately; increasing targetSdk is not a malware fix.

The appeal form asks for a contact email, package name, the APK SHA-256 of the
file uploaded to VirusTotal, and supporting details. No appeal or VirusTotal
upload has been submitted as part of this investigation.

## Primary references

- [Google developer guidance for Play Protect warnings](https://developers.google.com/android/play-protect/warning-dev-guidance)
- [Google Play Protect appeal form](https://support.google.com/googleplay/android-developer/contact/protectappeals)
- [Android manifest merging and implicit system permissions](https://developer.android.com/build/manage-manifests#implicit_system_permissions)
- [Moonlight release](https://github.com/moonlight-stream/moonlight-android/releases/tag/v12.2)
- [Artemis release](https://github.com/ClassicOldSong/moonlight-android/releases/tag/v20.2.6)
- [Hestia RC2 release](https://github.com/MrOz59/Hestia-Android/releases/tag/october-2026-rc2)
