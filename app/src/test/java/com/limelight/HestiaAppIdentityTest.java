package com.limelight;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ProviderInfo;

import androidx.test.core.app.ApplicationProvider;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

import static org.junit.Assert.*;

/**
 * Protects installation alongside official Moonlight and Artemis.
 * Source packages intentionally remain in the com.limelight namespace.
 */
@Config(sdk = 33, shadows = {
        com.limelight.shadows.ShadowMoonBridge.class,
        com.limelight.shadows.ShadowGameManager.class
})
@RunWith(RobolectricTestRunner.class)
public class HestiaAppIdentityTest {
    @Test
    public void usesIndependentApplicationIdForEveryBuildVariant() {
        String expected = "com.mroz59.hestia"
                + (BuildConfig.ROOT_BUILD ? ".root" : "")
                + (BuildConfig.DEBUG ? ".debug" : "");
        assertEquals("The installed package ID must belong to Hestia",
                expected, BuildConfig.APPLICATION_ID);
        assertNotEquals("com.limelight.noir", BuildConfig.APPLICATION_ID);
        assertNotEquals("com.limelight.root.noir", BuildConfig.APPLICATION_ID);
        assertNotEquals("com.limelight", BuildConfig.APPLICATION_ID);

        Context context = ApplicationProvider.getApplicationContext();
        assertEquals("Manifest package must match the Gradle application ID",
                expected, context.getPackageName());
    }

    @Test
    public void mergedManifestDoesNotRequestUnusedPhoneOrStorageAccess() throws Exception {
        Context context = ApplicationProvider.getApplicationContext();
        PackageInfo info = context.getPackageManager().getPackageInfo(
                context.getPackageName(), PackageManager.GET_PERMISSIONS);
        assertNotNull(info.requestedPermissions);
        for (String permission : info.requestedPermissions) {
            assertNotEquals("Phone state access is not used by Hestia",
                    "android.permission.READ_PHONE_STATE", permission);
            assertNotEquals("Imports use the Storage Access Framework",
                    "android.permission.READ_EXTERNAL_STORAGE", permission);
            assertNotEquals("Exports use the Storage Access Framework",
                    "android.permission.WRITE_EXTERNAL_STORAGE", permission);
        }
    }

    @Test
    public void posterProviderAuthorityFollowsApplicationId() throws Exception {
        Context context = ApplicationProvider.getApplicationContext();
        PackageInfo info = context.getPackageManager().getPackageInfo(
                context.getPackageName(), PackageManager.GET_PROVIDERS);

        String expectedAuthority = "poster." + BuildConfig.APPLICATION_ID;
        assertEquals(expectedAuthority, PosterContentProvider.AUTHORITY);
        assertNotNull("Merged manifest should declare content providers", info.providers);

        boolean found = false;
        for (ProviderInfo provider : info.providers) {
            if (expectedAuthority.equals(provider.authority)) {
                found = true;
                break;
            }
        }
        assertTrue("The poster provider must not collide with Artemis", found);
    }
}
