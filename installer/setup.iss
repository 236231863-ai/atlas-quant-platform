; Atlas Quant Platform - Inno Setup Installer
; 生成 Atlas_Setup.exe：安装向导 / 桌面快捷方式 / 开始菜单 / 卸载 / 升级

#define MyAppName "Atlas Quant Platform"
#define MyAppVersion "3.6.0"
#define MyAppPublisher "Atlas Quant Team"
#define MyAppExeName "Atlas.exe"
#define MyAppURL "https://github.com/236231863-ai/atlas-quant-platform"

[Setup]
AppId={{8A2F3C11-7B45-4E6A-9C1D-ATLASQUANT00001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=Atlas_Setup
SetupIconFile=..\branding\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
; 升级支持：使用上一版本安装目录
UsePreviousAppDir=yes
UsePreviousTasks=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\Atlas.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Atlas_CLI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Atlas_Worker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
