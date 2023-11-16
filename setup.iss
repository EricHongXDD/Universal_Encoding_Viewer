; 脚本由 Inno Setup 脚本向导 生成！
; 有关创建 Inno Setup 脚本文件的详细资料请查阅帮助文档！

#define MyAppName "字符编码查看软件"
#define MyAppVersion "1.0"
#define MyAppPublisher "Hong"
#define MyAppURL "https://github.com/EricHongXDD/Universal_Encoding_Viewer"
#define MyAppExeName "字符编码查看软件V1.0.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要为其他安装程序使用相同的AppId值。
; (若要生成新的 GUID，可在菜单中点击 "工具|生成 GUID"。)
AppId={{5DC83FD7-DFC0-4D84-A1F6-67C513EF6119}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; 以下行取消注释，以在非管理安装模式下运行（仅为当前用户安装）。
;PrivilegesRequired=lowest
OutputDir=C:\Users\10292
OutputBaseFilename=EncodingViewer_Setup_1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\10292\字符编码查看软件\字符编码查看软件V1.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_lzma.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_queue.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\base_library.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\libcrypto-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\libssl-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\python37.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\字符编码查看软件\certifi\*"; DestDir: "{app}\certifi"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\字符编码查看软件\charset_normalizer\*"; DestDir: "{app}\charset_normalizer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\字符编码查看软件\PyQt5\*"; DestDir: "{app}\PyQt5"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\字符编码查看软件\res\*"; DestDir: "{app}\res"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意: 不要在任何共享系统文件上使用“Flags: ignoreversion”

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

