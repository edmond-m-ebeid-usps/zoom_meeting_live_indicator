from pywinauto import Desktop
import time

print("Zoom Mic Detector")
print("-----------------")

while True:
    try:
        zoom_windows = Desktop(backend="uia").windows(
            title_re=".*Zoom.*",
            visible_only=True
        )

        mic_state = "UNKNOWN"

        for window in zoom_windows:
            # If Zoom shows "Mute", clicking it would mute us,
            # therefore the microphone is currently LIVE.
            mute_buttons = window.descendants(
                title="Mute",
                control_type="Button"
            )

            if mute_buttons:
                mic_state = "LIVE"
                break

            # If Zoom shows "Unmute", we're currently muted.
            unmute_buttons = window.descendants(
                title="Unmute",
                control_type="Button"
            )

            if unmute_buttons:
                mic_state = "MUTED"
                break

        if mic_state == "LIVE":
            print("\r🔴 MIC LIVE     ", end="", flush=True)
        elif mic_state == "MUTED":
            print("\rMIC MUTED       ", end="", flush=True)
        else:
            print("\rZoom state unknown", end="", flush=True)

    except Exception as e:
        print(f"\rError: {e}", end="", flush=True)

    time.sleep(0.25)
