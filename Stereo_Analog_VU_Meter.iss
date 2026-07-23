#define MyAppName "Stereo Analog VU Meter"
#define MyAppVersion "1.1"
#define MyAppExeName "Stereo Analog VU Meter.exe"

[Setup]
AppId={{A8E2C530-7D06-45EE-9A69-6AF2D03E9A7B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Stereo Analog VU Meter
DefaultGroupName={#MyAppName}
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=Stereo_Analog_VU_Meter.ico
OutputDir=installer
OutputBaseFilename=Stereo_Analog_VU_Meter_v1.1_Setup

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "Stereo_Analog_VU_Meter.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Stereo_Analog_VU_Meter.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Stereo_Analog_VU_Meter.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
