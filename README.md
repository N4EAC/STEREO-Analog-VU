# Stereo Analog VU Meter v1.0.1

A borderless Windows desktop application with two live stereo analog VU meters.

## Features

- Separate left and right analog VU meters
- Black meter background
- Red needles
- Purple dB scale markings
- Borderless custom window
- Drag the custom title bar to move the application
- Resize from the lower-right corner
- Double-click the title bar to maximize or restore
- Audio Setup dialog for selecting a Windows playback output
- Remembers the last window size, position, audio device, sample rate, and block size
- Live RMS audio metering

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- A stereo audio input device or loopback/virtual audio cable

## Run from source

1. Install dependencies:

   `pip install -r requirements.txt`

2. Start the application:

   `python stereo_vu_meter.py`

## Build a standalone EXE

Run:

`build_exe.bat`

The executable will be created in the `dist` folder.

## Audio routing

To meter computer playback rather than a Windows playback output, select a Windows loopback-capable device, Stereo Mix, or a virtual audio cable in Setup.

## v1.0.1 fixes

- Audio discovery and device opening now run outside the UI thread.
- Setup opens immediately even if a Windows audio driver is slow or unresponsive.
- Window dragging remains responsive while audio initializes.
- Close exits immediately without waiting for an audio driver to release.
- Setup is raised and focused reliably above the main window.

## Version 1.0.2

- Prevents an indefinite CONNECTING AUDIO status.
- Adds a five-second audio connection timeout.
- Prompts for audio selection instead of opening an unknown default device.

## Version 1.0.3

Corrected status-label color updates when applying audio settings.

## Version 1.1

Audio capture now uses Windows WASAPI loopback. Setup lists playback outputs only, including speakers, headphones, HDMI, and USB audio devices.
