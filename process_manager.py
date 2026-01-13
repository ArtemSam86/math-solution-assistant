import os
import sys
import signal
import atexit
from pathlib import Path

class ProcessManager:
    def __init__(self, pid_file='math_bot.pid'):
        self.pid_file = Path(pid_file)
        self.pid = os.getpid()
    
    def check_existing_process(self):
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                print(f"⚠️ Обнаружен предыдущий процесс {old_pid}")
                
                try:
                    os.kill(old_pid, signal.SIGTERM)
                    print(f"✅ Сигнал завершения отправлен")
                except ProcessLookupError:
                    print(f"ℹ️ Процесс {old_pid} уже завершен")
                
                self.pid_file.unlink(missing_ok=True)
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                self.pid_file.unlink(missing_ok=True)
    
    def create_pid_file(self):
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(self.pid))
            print(f"📝 PID файл создан: {self.pid_file}")
        except Exception as e:
            print(f"❌ Ошибка создания PID файла: {e}")
    
    def cleanup(self):
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    stored_pid = int(f.read().strip())
                
                if stored_pid == self.pid:
                    self.pid_file.unlink()
                    print("🗑️ PID файл удален")
            except:
                pass
    
    def register_handlers(self):
        def signal_handler(signum, frame):
            print(f"\n📶 Получен сигнал {signum}, завершаю работу...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        atexit.register(self.cleanup)