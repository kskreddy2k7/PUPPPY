import os
import sys
import subprocess

def create_desktop_app_shortcut():
    try:
        desktop_dir = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop_dir, 'Launch CutePuppy.lnk')

        exe_path = os.path.join(desktop_dir, 'CutePuppyApp', 'CutePuppy.exe')
        app_dir = os.path.join(desktop_dir, 'CutePuppyApp')

        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{exe_path}'
$Shortcut.WorkingDirectory = '{app_dir}'
$Shortcut.IconLocation = '{exe_path}, 0'
$Shortcut.Save()
"""
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        print(f"Desktop shortcut created at: {shortcut_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_desktop_app_shortcut()
