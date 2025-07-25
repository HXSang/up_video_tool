import subprocess

def supports_clipboard(serial="emulator-5554") -> bool:
    try:
        result = subprocess.run(
            ["adb", "-s", serial, "shell", "input", "clipboard", "test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3
        )
        return result.returncode == 0 and "Unknown option" not in result.stderr.decode()
    except Exception:
        return False

if __name__ == "__main__":
    serial = "emulator-5554"
    if supports_clipboard(serial):
        print(f"✅ Thiết bị {serial} HỖ TRỢ clipboard.")
    else:
        print(f"❌ Thiết bị {serial} KHÔNG hỗ trợ clipboard.")
