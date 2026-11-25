package com.limelight.hestia;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.junit.Test;

import java.util.List;

public class HestiaAppliedSettingsTest {
    private static JsonObject json(String text) {
        return JsonParser.parseString(text).getAsJsonObject();
    }

    @Test
    public void reportsOnlyWhatHermesOverrides() {
        List<HestiaAppliedSettings.Override> overrides = HestiaAppliedSettings.overrides(json(
                "{\"ok\":true,\"settings\":{"
                        + "\"virtual_display\":{\"requested\":false,\"effective\":true,\"source\":\"app_forced\"},"
                        + "\"scale_factor\":{\"requested\":100,\"effective\":100,\"source\":\"client\"}}}"));
        assertEquals(1, overrides.size());
        assertEquals(HestiaAppliedSettings.VIRTUAL_DISPLAY, overrides.get(0).setting);
        assertEquals(1, overrides.get(0).effective);
        assertEquals(HestiaAppliedSettings.Source.APP_FORCED, overrides.get(0).source);
    }

    @Test
    public void namesEachSource() {
        List<HestiaAppliedSettings.Override> overrides = HestiaAppliedSettings.overrides(json(
                "{\"settings\":{"
                        + "\"virtual_display\":{\"requested\":false,\"effective\":true,\"source\":\"isolated_session\"},"
                        + "\"scale_factor\":{\"requested\":100,\"effective\":50,\"source\":\"app\"}}}"));
        assertEquals(2, overrides.size());
        assertEquals(HestiaAppliedSettings.Source.ISOLATED_SESSION, overrides.get(0).source);
        assertEquals(HestiaAppliedSettings.SCALE_FACTOR, overrides.get(1).setting);
        assertEquals(50, overrides.get(1).effective);
        assertEquals(HestiaAppliedSettings.Source.HOST_SETTING, overrides.get(1).source);
    }

    @Test
    public void olderHermesWithoutSettingsReportsNothing() {
        assertTrue(HestiaAppliedSettings.overrides(json("{\"ok\":true}")).isEmpty());
        assertTrue(HestiaAppliedSettings.overrides(json("{\"ok\":true,\"settings\":null}")).isEmpty());
        assertTrue(HestiaAppliedSettings.overrides(null).isEmpty());
    }
}
