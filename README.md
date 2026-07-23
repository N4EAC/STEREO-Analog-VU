# Stereo Analog VU Meter v1.1.1

Borderless Windows stereo VU meter that captures the audio currently playing through a selected Windows speaker or headphone output.

## Fixes in v1.1.1

- Rebuilt from the corrected source rather than the older defective package.
- Replaced `sounddevice` endpoint handling with `soundcard` playback-loopback capture.
- Setup lists Windows playback devices only.
- Removed all invalid `StringVar.configure()` calls.
- Missing or changed saved devices fall back to the current Windows default output.
- Includes the application icon, EXE build script, and Inno Setup installer script.

## Run from source

1. Run `pip install -r requirements.txt`
2. Run `python stereo_vu_meter.py`
3. Open Setup and select the speaker/headphone output carrying the audio.

## Build

Run `build_exe.bat`. Compile `Stereo_Analog_VU_Meter.iss` after the EXE appears in `dist`.


## Build note

Keep `Stereo_Analog_VU_Meter.ico` in the same folder as `build_exe.bat`,
`requirements.txt`, and `stereo_vu_meter.py`. The corrected build script stops
with `BUILD FAILED` when any build step fails.


## Version 1.1.4 fixes

- Setup opens immediately and stays visible above the main window.
- Playback-output enumeration runs in the background so Setup cannot appear frozen.
- The main borderless window is given a real Windows taskbar entry.
- A unique Windows AppUserModelID and runtime window icon are applied.
- The build script now bundles the ICO inside the one-file executable.
