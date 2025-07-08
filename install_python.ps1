$ErrorActionPreference = 'Stop'
$pythonVersion = '3.10.11'
$installDir = 'C:\\Python310'
$installer = "python-$pythonVersion-amd64.exe"
$url = "https://www.python.org/ftp/python/$pythonVersion/$installer"

Write-Host "Downloading Python $pythonVersion..."
Invoke-WebRequest -Uri $url -OutFile $installer

Write-Host "Installing to $installDir..."
Start-Process -FilePath $installer -ArgumentList "InstallAllUsers=1 TargetDir=$installDir PrependPath=1 Include_test=0" -Wait

Remove-Item $installer
Write-Host "Python installed"
