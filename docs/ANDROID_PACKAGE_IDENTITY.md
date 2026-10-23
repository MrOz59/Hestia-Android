# Android package identity

Hestia Android intentionally keeps the Java/Android **namespace** `com.limelight` inherited from Moonlight/Artemis. Renaming Java packages is unrelated to the installed app's identity and would make upstream maintenance substantially harder.

Gradle assigns independent **application IDs** so Hestia can coexist with Artemis and official Moonlight:

| Variant | Android application ID |
| --- | --- |
| Non-root release | `com.mroz59.hestia` |
| Non-root debug | `com.mroz59.hestia.debug` |
| Root release | `com.mroz59.hestia.root` |
| Root debug | `com.mroz59.hestia.root.debug` |

Android's package name is the isolation boundary for app data, certificates, preferences, saved servers, and app updates. **Installing Hestia will not import or share Artemis pairing keys.** Pair the host independently in Hestia.

The poster content-provider authority uses `poster.${applicationId}`, and the app's Java implementation uses `BuildConfig.APPLICATION_ID`, so its authority stays unique for each variant. The `HestiaAppIdentityTest` checks this contract in CI.

Signing keys must remain stable for updates of the same release ID. APKs built by CI are unsigned-for-release debug artifacts, **not** production-distribution packages.

Hestia's visible name is now distinct, but the upstream icon artwork and several inherited explanatory strings are intentionally unchanged until the later visual identity and copy review. Preserve upstream author/license notices when replacing those assets.
