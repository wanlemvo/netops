param([long]$WindowHandle, [string]$Output)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class NativeCapture {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);
}
'@
$target = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$WindowHandle)
$deadline = [DateTime]::UtcNow.AddSeconds(40)
$loaded = $false
do {
    $elements = $target.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    $names = @($elements | ForEach-Object { $_.Current.Name })
    $loaded = ($names -contains 'Dashboard') -and ($names -contains 'People') -and ($names -contains 'Intel')
    if (-not $loaded) { Start-Sleep -Milliseconds 250 }
} until ($loaded -or [DateTime]::UtcNow -gt $deadline)
if (-not $loaded) { throw 'Native window did not expose the rendered Dashboard, People and Intel navigation.' }
$rect = New-Object NativeCapture+RECT
[void][NativeCapture]::GetWindowRect([IntPtr]$WindowHandle, [ref]$rect)
$bitmap = New-Object System.Drawing.Bitmap(($rect.Right-$rect.Left),($rect.Bottom-$rect.Top))
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$dc = $graphics.GetHdc()
try { $captured = [NativeCapture]::PrintWindow([IntPtr]$WindowHandle, $dc, 2) }
finally { $graphics.ReleaseHdc($dc); $graphics.Dispose() }
try {
    if (-not $captured) { throw 'Native window capture failed.' }
    $bitmap.Save($Output, [System.Drawing.Imaging.ImageFormat]::Png)
} finally { $bitmap.Dispose() }
Write-Output 'Native WebView2 Dashboard, People and Intel controls are rendered.'
