import time
import threading
import logging
from pynput import keyboard, mouse
import cv2
import numpy as np
from mss import mss
import os
import sys
from typing import Dict, Tuple
import argparse


class AutoFishing:
    def __init__(
        self,
        template_paths: Dict[str, str],
        detection_threshold: float = 0.9,
        detection_interval: float = 0.3,
        base_click_interval: float = 0.01,
        safe_release_delay: float = 0.15,
        region_of_interest: Tuple[int, int, int, int] = (1250, 500, 1800, 1500),
        log_file: str = "fishing_automation.log",
        retry_attempts: int = 3,
        retry_delay: float = 0.1,
        debug: bool = False
    ):
        self.threshold = detection_threshold
        self.detection_interval = detection_interval
        self.base_click_interval = base_click_interval
        self.safe_release_delay = safe_release_delay
        self.roi = region_of_interest
        self.template_paths = template_paths
        self.templates = {}
        self.stop_event = threading.Event()
        self.is_clicking = False
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.debug = debug

        self._configure_logging(log_file, self.debug)
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self._load_templates()

    def _configure_logging(self, log_file: str, debug: bool):
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger()
        self.logger.info("Logging telah dikonfigurasi.")
        if debug:
            self.logger.debug("Mode DEBUG diaktifkan.")

    def _load_templates(self):
        self.logger.info("Memuat template gambar...")
        for name, path in self.template_paths.items():
            if not os.path.isfile(path):
                self.logger.error(f"Gambar template '{path}' tidak ditemukan.")
                sys.exit(1)
            template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                self.logger.error(f"Gagal memuat gambar template '{path}'.")
                sys.exit(1)
            self.templates[name] = template
            self.logger.info(f"Template '{name}' berhasil dimuat.")
            self.logger.debug(f"Detail template '{name}': {template.shape}")
        self.logger.info("Semua template berhasil dimuat.")

    def _is_template_on_screen(self, sct: mss, monitor: Dict[str, int], template: np.ndarray, retries: int = 3) -> bool:
        for attempt in range(retries):
            try:
                screen = np.array(sct.grab(monitor))
                gray_screenshot = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                match_result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(match_result >= self.threshold)
                found = len(locations[0]) > 0
                if found:
                    self.logger.info(f"Template ditemukan pada percobaan {attempt + 1}.")
                else:
                    self.logger.debug(f"Template tidak ditemukan pada percobaan {attempt + 1}.")
                return found
            except Exception as e:
                self.logger.warning(f"Percobaan {attempt + 1}: Gagal mendeteksi template karena {e}. Mencoba lagi...")
                time.sleep(self.retry_delay)
        self.logger.error("Gagal mendeteksi template setelah beberapa percobaan.")
        return False

    def _on_key_press(self, key):
        try:
            if key.char == 'q':
                self.logger.info("Tombol 'q' ditekan. Menghentikan skrip...")
                self.stop_event.set()
                return False
        except AttributeError:
            pass

    def _calculate_click_interval(self, sct: mss, monitor: Dict[str, int]) -> float:
        template_image_3 = self.templates.get("image_3")
        if template_image_3 is not None and self._is_template_on_screen(sct, monitor, template_image_3):
            self.logger.info("Mode klik cepat diaktifkan.")
            if self.debug:
                self.logger.debug(f"Menggunakan interval klik: {self.base_click_interval * 0.5:.4f} detik")
            return self.base_click_interval * 0.5
        self.logger.info("Mode klik lambat diaktifkan.")
        if self.debug:
            self.logger.debug(f"Menggunakan interval klik: {self.base_click_interval * 1.5:.4f} detik")
        return self.base_click_interval * 1.5

    def _mouse_control_loop(self):
        try:
            with mss() as sct:
                monitor = {
                    "top": self.roi[1],
                    "left": self.roi[0],
                    "width": self.roi[2] - self.roi[0],
                    "height": self.roi[3] - self.roi[1]
                }

                self.logger.info("Memulai loop kontrol mouse...")
                first_detection = True
                while not self.stop_event.is_set():
                    if first_detection:
                        self.logger.info("Mode rendah daya diaktifkan untuk deteksi pertama.")
                        current_detection_interval = self.detection_interval * 2
                    else:
                        current_detection_interval = self.detection_interval

                    template_image_1 = self.templates.get("image_1")
                    if template_image_1 is not None and self._is_template_on_screen(sct, monitor, template_image_1):
                        template_image_2 = self.templates.get("image_2")
                        if template_image_2 is not None and self._is_template_on_screen(sct, monitor, template_image_2):
                            self.logger.info("Bar pancing minimum terdeteksi. Menunggu hingga hilang...")
                            while self._is_template_on_screen(sct, monitor, template_image_2) and not self.stop_event.is_set():
                                time.sleep(0.1)
                            self.logger.info("Bar pancing minimum telah hilang. Memulai mekanik pemancingan...")

                        while not self.stop_event.is_set():
                            template_image_3 = self.templates.get("image_3")
                            if template_image_3 is not None and self._is_template_on_screen(sct, monitor, template_image_3):
                                if self.is_clicking:
                                    self.mouse_controller.release(mouse.Button.left)
                                    self.is_clicking = False
                                    self.logger.info("Mouse dilepaskan.")
                                    self.logger.debug("Tombol mouse dilepaskan.")
                            else:
                                if not self.is_clicking:
                                    self.mouse_controller.press(mouse.Button.left)
                                    self.is_clicking = True
                                    self.logger.info("Mouse ditekan.")
                                    self.logger.debug("Tombol mouse ditekan.")

                            current_interval = self._calculate_click_interval(sct, monitor)
                            time.sleep(current_interval)

                            if not (template_image_1 is not None and self._is_template_on_screen(sct, monitor, template_image_1)):
                                self.logger.info("Bar pancing tidak terdeteksi. Melakukan tindakan penangkapan ikan...")
                                time.sleep(2)
                                template_image_4 = self.templates.get("image_4")
                                if template_image_4 is not None and self._is_template_on_screen(sct, monitor, template_image_4):
                                    self.mouse_controller.press(mouse.Button.left)
                                    time.sleep(self.safe_release_delay)
                                    self.mouse_controller.release(mouse.Button.left)
                                    self.logger.info("Ikan berhasil ditangkap.")
                                    self.logger.debug("Mouse ditekan dan dilepaskan untuk menangkap ikan.")
                                    time.sleep(1)

                                self.mouse_controller.press(mouse.Button.left)
                                time.sleep(3)
                                self.mouse_controller.release(mouse.Button.left)
                                self.logger.info("Tindakan penangkapan ikan selesai.")
                                self.logger.debug("Mouse ditekan dan dilepaskan setelah penangkapan ikan.")

                                time.sleep(1)

                                while not self.stop_event.is_set():
                                    template_image_1_reset = self.templates.get("image_1")
                                    if template_image_1_reset is not None and self._is_template_on_screen(sct, monitor, template_image_1_reset):
                                        if self.is_clicking:
                                            self.mouse_controller.release(mouse.Button.left)
                                            self.is_clicking = False
                                            self.logger.info("Mouse dilepaskan setelah reset.")
                                            self.logger.debug("Tombol mouse dilepaskan setelah reset.")
                                        self.logger.info("Kembali ke status normal.")
                                        self.logger.debug("Status aplikasi kembali normal.")
                                        break
                                    time.sleep(self.detection_interval)

                                if not self.is_clicking:
                                    self.mouse_controller.press(mouse.Button.left)
                                    self.is_clicking = True
                                    self.logger.info("Mouse ditekan kembali setelah reset.")
                                    self.logger.debug("Tombol mouse ditekan kembali setelah reset.")
                    time.sleep(current_detection_interval)
                    first_detection = False
        except Exception as e:
            self.logger.error(f"Terjadi kesalahan dalam kontrol mouse: {e}")
            if self.debug:
                self.logger.debug("Traceback:", exc_info=True)
        finally:
            if self.is_clicking:
                self.mouse_controller.release(mouse.Button.left)
                self.logger.info("Mouse dilepaskan pada akhir skrip.")
                self.logger.debug("Tombol mouse dilepaskan pada akhir skrip.")
            self.logger.info("Loop kontrol mouse dihentikan.")

    def start(self):
        keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        keyboard_listener.start()
        self.logger.info("Listener keyboard dimulai. Tekan 'q' untuk menghentikan.")

        mouse_thread = threading.Thread(target=self._mouse_control_loop, name="MouseControlThread")
        mouse_thread.start()

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt diterima. Menghentikan skrip...")
            self.stop_event.set()
        finally:
            mouse_thread.join()
            keyboard_listener.stop()
            self.logger.info("Skrip dihentikan dengan aman.")


def main():
    parser = argparse.ArgumentParser(description="Skrip Otomasi Pemancingan")
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Aktifkan mode debug untuk logging lebih rinci.'
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    TEMPLATE_DIR = os.path.join(project_root, 'assets')

    TEMPLATE_FILES = {
        "image_1": 'digigit.png',
        "image_2": 'bar_minimum.png',
        "image_3": 'bar_maksimum.png',
        "image_4": 'ikan_baru.png'
    }

    template_paths = {key: os.path.join(TEMPLATE_DIR, filename) for key, filename in TEMPLATE_FILES.items()}

    if not all(os.path.isfile(path) for path in template_paths.values()):
        logging.error("Salah satu atau lebih template gambar tidak ditemukan di direktori 'assets'.")
        sys.exit(1)

    fishing_bot = AutoFishing(
        template_paths=template_paths,
        detection_threshold=0.9,
        detection_interval=0.3,
        base_click_interval=0.01,
        safe_release_delay=0.15,
        region_of_interest=(1250, 500, 1800, 1500),
        log_file="fishing_automation.log",
        debug=args.debug
    )
    fishing_bot.start()


if __name__ == "__main__":
    main()
