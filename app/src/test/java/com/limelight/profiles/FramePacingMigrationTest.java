package com.limelight.profiles;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.test.core.app.ApplicationProvider;

import com.limelight.preferences.PreferenceConfiguration;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import static org.junit.Assert.*;

/**
 * The frame pacing selection used to be overridden to Balanced, while "latency" was the
 * stored default. These tests cover the one-time migration that keeps everyone on Balanced
 * unless they choose otherwise afterwards.
 */
@Config(sdk = {33}, shadows = {com.limelight.shadows.ShadowMoonBridge.class, com.limelight.shadows.ShadowGameManager.class})
@RunWith(RobolectricTestRunner.class)
public class FramePacingMigrationTest {
    private static final String KEY = "frame_pacing";
    private static final String MARKER = "frame_pacing_respected_v1";

    private Context context;
    private SharedPreferences base;

    @Before
    public void setUp() {
        context = ApplicationProvider.getApplicationContext();
        ProfilesManager.instance = null;
        deleteRecursively(new File(context.getFilesDir(), "profiles"));
        base = androidx.preference.PreferenceManager.getDefaultSharedPreferences(context);
        base.edit().clear().commit();
        PreferenceConfiguration.resetFramePacingMigrationForTesting();
    }

    private int pacing() {
        return PreferenceConfiguration.readPreferences(context).framePacing;
    }

    private void newProcess() {
        ProfilesManager.instance = null;
        ProfilesManager.getInstance().load(context);
        PreferenceConfiguration.resetFramePacingMigrationForTesting();
    }

    @Test
    public void storedOldDefaultBecomesBalanced() {
        base.edit().putString(KEY, "latency").commit();
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
        assertEquals("balanced", base.getString(KEY, null));
        assertTrue(base.getBoolean(MARKER, false));
    }

    @Test
    public void noStoredValueDefaultsToBalanced() {
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
    }

    @Test
    public void latencyChosenAfterMigrationIsRespected() {
        base.edit().putString(KEY, "latency").commit();
        pacing();
        base.edit().putString(KEY, "latency").commit();
        newProcess();
        assertEquals(PreferenceConfiguration.FRAME_PACING_MIN_LATENCY, pacing());
    }

    @Test
    public void otherSelectionsAreUntouched() {
        base.edit().putString(KEY, "smoothness").commit();
        assertEquals(PreferenceConfiguration.FRAME_PACING_MAX_SMOOTHNESS, pacing());
        base.edit().putString(KEY, "cap-fps").commit();
        assertEquals(PreferenceConfiguration.FRAME_PACING_CAP_FPS, pacing());
    }

    @Test
    public void warpKeepsBalancedAndItsFactor() {
        base.edit().putString(KEY, "warp").commit();
        PreferenceConfiguration config = PreferenceConfiguration.readPreferences(context);
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, config.framePacing);
        assertEquals(2, config.framePacingWarpFactor);
        base.edit().putString(KEY, "warp2").commit();
        config = PreferenceConfiguration.readPreferences(context);
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, config.framePacing);
        assertEquals(4, config.framePacingWarpFactor);
    }

    @Test
    public void unknownValueFallsBackToBalanced() {
        base.edit().putString(KEY, "something-else").commit();
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
    }

    @Test
    public void activeProfileWithOldDefaultIsMigratedAndPersisted() {
        Map<String, Object> options = new HashMap<>();
        options.put(KEY, "latency");
        SettingsProfile profile = new SettingsProfile(UUID.randomUUID(), "Old", 0, 0, options);
        ProfilesManager pm = ProfilesManager.getInstance();
        pm.add(profile);
        pm.setActive(profile.getUuid());
        pm.save(context);

        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());

        // After a restart the profile, as saved, still says Balanced and is marked migrated.
        newProcess();
        SettingsProfile reloaded = ProfilesManager.getInstance().getActive();
        assertNotNull(reloaded);
        assertEquals("balanced", reloaded.getOptions().get(KEY));
        assertEquals(Boolean.TRUE, reloaded.getOptions().get(MARKER));
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
    }

    @Test
    public void profileLatencyChosenAfterMigrationIsRespected() {
        // A profile created after the migration copies the global settings, marker included.
        pacing();
        Map<String, Object> options = new HashMap<>(base.getAll());
        options.put(KEY, "latency");
        SettingsProfile profile = new SettingsProfile(UUID.randomUUID(), "New", 0, 0, options);
        ProfilesManager pm = ProfilesManager.getInstance();
        pm.add(profile);
        pm.setActive(profile.getUuid());
        pm.save(context);

        newProcess();
        assertEquals(PreferenceConfiguration.FRAME_PACING_MIN_LATENCY, pacing());
    }

    @Test
    public void legacyOptionInProfileIsConverted() {
        base.edit().putString(KEY, "balanced").commit();
        Map<String, Object> options = new HashMap<>();
        options.put("checkbox_disable_frame_drop", false);
        SettingsProfile profile = new SettingsProfile(UUID.randomUUID(), "Legacy", 0, 0, options);
        ProfilesManager pm = ProfilesManager.getInstance();
        pm.add(profile);
        pm.setActive(profile.getUuid());
        pm.save(context);

        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
        assertFalse(pm.getActive().getOptions().containsKey("checkbox_disable_frame_drop"));
        // Reading again must not rewrite the global value.
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
        assertEquals("balanced", base.getString(KEY, null));
    }

    @Test
    public void legacyOptionInProfileAfterGlobalMigrationKeepsGlobalValue() {
        // Global settings already migrated in an earlier run.
        base.edit().putString(KEY, "balanced").commit();
        pacing();
        assertTrue(base.getBoolean(MARKER, false));

        Map<String, Object> options = new HashMap<>();
        options.put("checkbox_disable_frame_drop", false);
        SettingsProfile profile = new SettingsProfile(UUID.randomUUID(), "OldLegacy", 0, 0, options);
        ProfilesManager pm = ProfilesManager.getInstance();
        pm.add(profile);
        pm.setActive(profile.getUuid());
        pm.save(context);

        newProcess();
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
        assertEquals("balanced", base.getString(KEY, null));
        assertFalse(ProfilesManager.getInstance().getActive().getOptions().containsKey("checkbox_disable_frame_drop"));
    }

    @Test
    public void legacyOptionInGlobalSettingsIsConverted() {
        base.edit().putBoolean("checkbox_disable_frame_drop", false).commit();
        assertEquals(PreferenceConfiguration.FRAME_PACING_BALANCED, pacing());
        assertFalse(base.contains("checkbox_disable_frame_drop"));
        assertEquals("balanced", base.getString(KEY, null));
    }

    private void deleteRecursively(File f) {
        if (f == null || !f.exists()) return;
        if (f.isDirectory()) {
            File[] children = f.listFiles();
            if (children != null) {
                for (File c : children) deleteRecursively(c);
            }
        }
        //noinspection ResultOfMethodCallIgnored
        f.delete();
    }
}
