import threading
import time

class ActionSync:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {}

    def mark(self, key, serial, status="done"):
        with self.lock:
            if serial not in self.state:
                self.state[serial] = {}
            self.state[serial][key] = status
            print(f"[SYNC] 🔖 {serial} => {key}: {status}")

    def wait_threshold(self, key, threshold=0.6, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                total = len([v for v in self.state.values() if v.get(key) != "failed"])
                done = sum(1 for v in self.state.values() if v.get(key) == "done")
                if total > 0 and done / total >= threshold:
                    print(f"[SYNC] ✅ Đã đạt {done}/{total} ({done/total:.0%}) ở bước {key}")
                    return
                else:
                    print(f"[SYNC] ⏳ {done}/{total} máy đã xong bước {key} (chờ {threshold*100:.0f}%)")
            time.sleep(1)
        print(f"[SYNC] ⏱ Timeout sau {timeout}s ở bước '{key}'")

    def get_failed_serials(self, key):
        with self.lock:
            return [s for s, v in self.state.items() if v.get(key) == "failed"]

    def get_done_serials(self, key):
        with self.lock:
            return [s for s, v in self.state.items() if v.get(key) == "done"]

    def reset(self):
        with self.lock:
            self.state.clear()
            print("[SYNC] 🔄 Đã reset trạng thái")
            
    def auto_fail_inactive(self, key, timeout=180):
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                waiting = [s for s, st in self.state.items() if key not in st]
                if not waiting:
                    return
            time.sleep(1)

        with self.lock:
            for s in self.state:
                if key not in self.state[s]:
                    print(f"[SYNC] ⏱ Auto fail {s} tại bước {key} (timeout {timeout}s)")
                    self.state[s][key] = "failed"

