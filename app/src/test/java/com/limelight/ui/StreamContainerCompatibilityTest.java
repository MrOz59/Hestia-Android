package com.limelight.ui;

import android.app.ActivityManager;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.pm.ConfigurationInfo;
import android.view.SurfaceView;

import androidx.test.core.app.ApplicationProvider;

import com.limelight.Game;
import com.limelight.preferences.PreferenceConfiguration;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = 31, shadows = {
        com.limelight.shadows.ShadowMoonBridge.class,
        com.limelight.shadows.ShadowGameManager.class
})
public class StreamContainerCompatibilityTest {
    private Context deviceWithGles(Integer version) {
        Context base = ApplicationProvider.getApplicationContext();
        ActivityManager manager = mock(ActivityManager.class);
        ConfigurationInfo info = null;
        if (version != null) {
            info = new ConfigurationInfo();
            info.reqGlEsVersion = version;
        }
        when(manager.getDeviceConfigurationInfo()).thenReturn(info);
        return new ContextWrapper(base) {
            @Override
            public Object getSystemService(String name) {
                return ACTIVITY_SERVICE.equals(name) ? manager : super.getSystemService(name);
            }
        };
    }

    private StreamContainer startStream(Context context, int requestedMode) {
        PreferenceConfiguration preferences = new PreferenceConfiguration();
        preferences.renderMode = requestedMode;
        StreamContainer container = new StreamContainer(context, null);
        container.init(mock(Game.class), preferences);
        // A temporary device limitation must not overwrite the user's saved preference.
        assertEquals(requestedMode, preferences.renderMode);
        return container;
    }

    @Test
    public void normalStreamingUsesSurfaceViewWithoutGles3() {
        StreamContainer container = startStream(deviceWithGles(0x00020000), 0);
        assertEquals(SurfaceView.class, container.getSurfaceView().getClass());
    }

    @Test
    public void both3dModesFallBackBeforeCreatingAGlesRenderer() {
        for (int mode : new int[]{1, 2}) {
            StreamContainer container = startStream(deviceWithGles(0x00020000), mode);
            assertEquals(SurfaceView.class, container.getSurfaceView().getClass());
        }
    }

    @Test
    public void unknownGraphicsCapabilitiesStillAllowNormalStreaming() {
        StreamContainer container = startStream(deviceWithGles(null), 2);
        assertEquals(SurfaceView.class, container.getSurfaceView().getClass());
    }

    @Test
    public void capableDevicesRemainEligibleForOptional3dRendering() {
        assertTrue(StreamContainer.supportsAdvancedRendering(deviceWithGles(0x00030000)));
        assertTrue(StreamContainer.supportsAdvancedRendering(deviceWithGles(0x00030002)));
        assertFalse(StreamContainer.supportsAdvancedRendering(deviceWithGles(0x00020000)));
    }
}
