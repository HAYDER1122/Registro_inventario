; Instalador para Sistema de Inventario v1
; Creado con Inno Setup
; Instrucciones: Abre este archivo con Inno Setup Compiler y presiona "Compile"

#define MyAppName "Sistema de Inventario"
#define MyAppVersion "1.0"
#define MyAppPublisher "HOPD"
#define MyAppExeName "Inventario.exe"
#define MyAppSourcePath "dist\"

[Setup]
AppId={{3E3F7D5E-5A5B-4C8D-9E2F-1A2B3C4D5E6F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=instaladores
OutputBaseFilename=SistemaInventario_v1_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=Logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"


[Files]
Source: "{#MyAppSourcePath}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSourcePath}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "inventario_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"; 

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Borrar todos los archivos de la carpeta de instalación
Type: files; Name: "{app}\*.*"
; Borrar carpeta de instalación
Type: dirifempty; Name: "{app}"
; Borrar datos del usuario en LOCALAPPDATA
Type: files; Name: "{localappdata}\{#MyAppName}\*.*"
Type: dirifempty; Name: "{localappdata}\{#MyAppName}"

[Registry]
Root: "HKCU"; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekey
