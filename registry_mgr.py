import winreg
import subprocess
import os

KEY_PATH = r"SOFTWARE\NVIDIA Corporation\Global\NGXCore"
VALUE_NAME = "ShowDlssIndicator"
TASK_NAME = "RevertDLSSIndicator"

def set_dlss_indicator(enable: bool):
    try:
        # Create key if it doesn't exist
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, KEY_PATH)
        
        # Open the key for writing
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY_PATH, 0, winreg.KEY_SET_VALUE)
        
        value = 1024 if enable else 0
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)
        return True, ""
    except Exception as e:
        return False, str(e)

def schedule_removal_task():
    # We use PowerShell to accurately compute exactly 4 hours from now and register a SYSTEM task.
    ps_cmd = f"""
    $Time = (Get-Date).AddHours(4)
    $Action = New-ScheduledTaskAction -Execute "reg.exe" -Argument "add `"HKLM\\{KEY_PATH}`" /v {VALUE_NAME} /t REG_DWORD /d 0 /f"
    $Trigger = New-ScheduledTaskTrigger -Once -At $Time
    Register-ScheduledTask -TaskName "{TASK_NAME}" -Trigger $Trigger -Action $Action -User "NT AUTHORITY\\SYSTEM" -RunLevel Highest -Force
    """
    
    try:
        # Run PS command
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, startupinfo=startupinfo
        )
        if result.returncode != 0:
            return False, f"PowerShell Error: {result.stderr}"
        return True, ""
    except Exception as e:
        return False, str(e)

def remove_scheduled_task():
    ps_cmd = f'Unregister-ScheduledTask -TaskName "{TASK_NAME}" -Confirm:$false -ErrorAction SilentlyContinue'
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, startupinfo=startupinfo
        )
    except Exception:
        pass
