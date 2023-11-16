; �ű��� Inno Setup �ű��� ���ɣ�
; �йش��� Inno Setup �ű��ļ�����ϸ��������İ����ĵ���

#define MyAppName "�ַ�����鿴���"
#define MyAppVersion "1.0"
#define MyAppPublisher "Hong"
#define MyAppURL "https://github.com/EricHongXDD/Universal_Encoding_Viewer"
#define MyAppExeName "�ַ�����鿴���V1.0.exe"

[Setup]
; ע: AppId��ֵΪ������ʶ��Ӧ�ó���
; ��ҪΪ������װ����ʹ����ͬ��AppIdֵ��
; (��Ҫ�����µ� GUID�����ڲ˵��е�� "����|���� GUID"��)
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
; ������ȡ��ע�ͣ����ڷǹ���װģʽ�����У���Ϊ��ǰ�û���װ����
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
Source: "C:\Users\10292\�ַ�����鿴���\�ַ�����鿴���V1.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_lzma.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_queue.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\base_library.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\libcrypto-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\libssl-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\python37.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\10292\�ַ�����鿴���\certifi\*"; DestDir: "{app}\certifi"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\�ַ�����鿴���\charset_normalizer\*"; DestDir: "{app}\charset_normalizer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\�ַ�����鿴���\PyQt5\*"; DestDir: "{app}\PyQt5"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\10292\�ַ�����鿴���\res\*"; DestDir: "{app}\res"; Flags: ignoreversion recursesubdirs createallsubdirs
; ע��: ��Ҫ���κι���ϵͳ�ļ���ʹ�á�Flags: ignoreversion��

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

