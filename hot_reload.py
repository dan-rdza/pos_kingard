# hot_reload.py
import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AppReloadHandler(FileSystemEventHandler):
    def __init__(self, app_process):
        self.app_process = app_process
    
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\n📁 Cambio detectado en {event.src_path}")
            print("🔄 Recargando aplicación...")
            
            # Terminar proceso actual
            self.app_process.terminate()
            self.app_process.wait()
            
            # Reiniciar la aplicación
            self.app_process = subprocess.Popen([sys.executable, "main.py"])
            return self.app_process

def main():
    # Iniciar la aplicación por primera vez
    app_process = subprocess.Popen([sys.executable, "main.py"])
    
    # Configurar observer para monitorear cambios
    event_handler = AppReloadHandler(app_process)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        app_process.terminate()
    observer.join()

if __name__ == "__main__":
    main()