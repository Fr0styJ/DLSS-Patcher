import sys
import ctypes
import traceback
from ui import App

def exception_hook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
    input("Press Enter to exit...")

sys.excepthook = exception_hook

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        try:
            print("Requesting UAC Elevation...")
            if sys.argv[0].endswith(".py"):
                args = " ".join([f'"{a}"' for a in sys.argv])
                # Note: passing sys.executable directly to ShellExecuteW works best unquoted for the lpFile parameter when using 'runas', but if that fails we have the prompt.
                result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
            else:
                result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.argv[0], "", None, 1)
            
            if result <= 32:
                print(f"Elevation failed with error code: {result}")
                input("Press Enter to exit...")
        except Exception as e:
            print("Elevation Error:", e)
            input("Press Enter to exit...")
        sys.exit(0)

    app = App()
    app.mainloop()
