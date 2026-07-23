#define MyAppName "Stereo Analog VU Meter"
#define MyAppVersion "1.1.4"
#define MyAppPublisher "Eduardo A. de Carvalho"
#define MyAppExeName "Stereo Analog VU Meter.exe"

[Setup]
AppId={{0E9C7B42-0FF1-4B7A-8CF6-789138944B3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Stereo Analog VU Meter
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=Stereo_Analog_VU_Meter_Setup_v1.1.4
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=Stereo_Analog_VU_Meter.ico
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
