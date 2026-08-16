import os
import sys
import subprocess

def create_desktop_shortcut():
    try:
        desktop_dir = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop_dir, 'CutePuppy.lnk')

        pythonw_path = os.path.join(sys.prefix, 'pythonw.exe')
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.py'))
        app_dir = os.path.dirname(app_path)

        # Use Windows PowerShell WScript.Shell COM Object to create authentic .lnk binary shortcut
        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{pythonw_path}'
$Shortcut.Arguments = '"{app_path}"'
$Shortcut.WorkingDirectory = '{app_dir}'
$Shortcut.IconLocation = '{pythonw_path}, 0'
$Shortcut.Save()
"""
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        print(f"Windows .lnk Desktop shortcut created successfully at: {shortcut_path}")
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")

if __name__ == "__main__":
    create_desktop_shortcut()
