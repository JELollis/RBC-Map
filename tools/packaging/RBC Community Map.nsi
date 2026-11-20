!include MUI2.nsh
!include LogicLib.nsh

!define PRODUCT_NAME "RBC Community Map"
!define PRODUCT_VERSION "1.0.4"
!define PRODUCT_PUBLISHER "RBC Community Map Team"
!define PRODUCT_WEB_SITE "https://github.com/JELollis/RBC-Map"
!define APP_EXE "RBC Community Map.exe"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "RBC-Map-Installer-${PRODUCT_VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\RBC-Map"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Main application" SecMain
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "build\windows\main_1.0.4.dist\*.*"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\images\favicon.ico" 0
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\images\favicon.ico" 0
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"
    ; Deliberately preserve %LOCALAPPDATA%\RBC-Map user data.
SectionEnd

VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalTrademarks" "Licensed under the Apache License, Version 2.0"
VIAddVersionKey "URLInfoAbout" "${PRODUCT_WEB_SITE}"
