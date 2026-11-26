package com.limelight.hestia;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * What Hermes will apply for the settings Hestia asked for, from the
 * {@code settings} object of a session/prepare response. Hermes reports, for
 * each setting it can override, the requested and effective values and who
 * decided. Only overrides are kept: a setting Hermes applies as asked needs no
 * notice.
 */
public final class HestiaAppliedSettings {
    /** Who decided a setting Hestia did not get as asked. */
    public enum Source {
        /** The host app forces its own setting on every client. */
        APP_FORCED,
        /** The app always runs on a virtual display of its own. */
        ISOLATED_SESSION,
        /** The host has no monitor, so it always uses a virtual display. */
        HEADLESS,
        /** A host or app setting applied (Hermes did not use the client's value). */
        HOST_SETTING,
    }

    /** One setting Hermes will not apply as requested. */
    public static final class Override {
        public final String setting;
        public final int effective;
        public final Source source;

        Override(String setting, int effective, Source source) {
            this.setting = setting;
            this.effective = effective;
            this.source = source;
        }
    }

    public static final String VIRTUAL_DISPLAY = "virtual_display";
    public static final String SCALE_FACTOR = "scale_factor";

    private HestiaAppliedSettings() {}

    /**
     * The overrides in a session/prepare response, in a fixed order
     * (virtual display, then scale). Empty for an older Hermes that does not
     * report them, or when everything is applied as asked.
     */
    public static List<Override> overrides(JsonObject response) {
        if (response == null || !(response.get("settings") instanceof JsonObject)) {
            return Collections.emptyList();
        }
        JsonObject settings = response.getAsJsonObject("settings");
        List<Override> result = new ArrayList<>();
        addIfOverridden(result, settings, VIRTUAL_DISPLAY);
        addIfOverridden(result, settings, SCALE_FACTOR);
        return result;
    }

    private static void addIfOverridden(List<Override> out, JsonObject settings, String name) {
        if (!(settings.get(name) instanceof JsonObject)) {
            return;
        }
        JsonObject setting = settings.getAsJsonObject(name);
        Integer requested = number(setting.get("requested"));
        Integer effective = number(setting.get("effective"));
        if (requested == null || effective == null || requested.equals(effective)) {
            return;
        }
        out.add(new Override(name, effective, source(HestiaCapabilities.string(setting, "source"))));
    }

    /** A boolean as 0/1, or an integer; null for anything else. */
    private static Integer number(JsonElement element) {
        if (element == null || !element.isJsonPrimitive()) {
            return null;
        }
        try {
            if (element.getAsJsonPrimitive().isBoolean()) {
                return element.getAsBoolean() ? 1 : 0;
            }
            if (element.getAsJsonPrimitive().isNumber()) {
                return element.getAsInt();
            }
        } catch (NumberFormatException | UnsupportedOperationException e) {
            return null;
        }
        return null;
    }

    private static Source source(String name) {
        if ("app_forced".equals(name)) {
            return Source.APP_FORCED;
        }
        if ("isolated_session".equals(name)) {
            return Source.ISOLATED_SESSION;
        }
        if ("headless".equals(name)) {
            return Source.HEADLESS;
        }
        return Source.HOST_SETTING;
    }
}
