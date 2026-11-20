"""
Heretic Version C - Video source abstraction

open_video_source(kind, url) → source co .read()/.isOpened()/.release()
(giao dien nhu cv2.VideoCapture — heretic_phase4_hud.py dung chung 1 duong ma).

Kinds:
  webcam : index camera ("0")
  rtsp   : RTSP URL (FFMPEG, buffer 1 — lay khung moi nhat, giam delay)
  uvc    : duong dan thiet bi UVC
  file   : duong dan file video
  window : capture window tren man hinh theo title (AirPlayReceiver/scrcp)
           — Windows only (mss + pywin32)
"""
import time

import cv2
import numpy as np

KINDS = ("webcam", "rtsp", "uvc", "file", "window")


class Cv2Source:
    """cv2.VideoCapture — webcam/rtsp/uvc/file."""

    def __init__(self, kind, url, width=None, height=None):
        if kind == "rtsp":
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            # buffer 1 khung: luon lay khung moi nhat, tan delay gom buffer
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        elif kind == "webcam":
            cap = cv2.VideoCapture(int(url))
            if width and height:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        else:  # uvc / file
            cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise RuntimeError(f"video source '{kind}' '{url}' khong mo duoc")
        self.cap = cap

    def read(self):
        return self.cap.read()

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.cap.release()


class WindowSource:
    """Capture window theo title (mss + pywin32) — Windows only.

    De mirror screen (AirPlayReceiver/scrcp): title window chua substring `url`.
    Re-query rect moi khung vi window co the di chuyen/resize.
    """

    def __init__(self, title):
        import ctypes
        import mss
        import win32gui
        try:
            # mss lay pixel thuc, win32gui lay don vi logich → phai DPI-aware
            # de 2 toa do trung nhau
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

        def find_window():
            found = []

            def _cb(hwnd, _):
                text = win32gui.GetWindowText(hwnd)
                if win32gui.IsWindowVisible(hwnd) and title.lower() in text.lower():
                    found.append(hwnd)

            win32gui.EnumWindows(_cb, None)
            return found[0] if found else None

        hwnd = find_window()
        if hwnd is None:
            raise RuntimeError(f"khong tim thay window hien thi chua title '{title}'")
        self._gui = win32gui
        self.hwnd = hwnd
        self._sct = mss.mss()

    def read(self):
        rect = self._gui.GetWindowRect(self.hwnd)
        frame = np.asarray(self._sct.grab(rect))[:, :, :3]  # BGRA → BGR
        return True, frame

    def isOpened(self):
        return self._gui.IsWindow(self.hwnd)

    def release(self):
        self._sct.close()


def open_video_source(kind, url, width=None, height=None):
    """Mo nguon video theo kind. url = index/duong dan/title (tuong ung moi kind)."""
    if kind not in KINDS:
        raise ValueError(f"kind '{kind}' khong hop le — cho phep: {', '.join(KINDS)}")
    if kind == "window":
        return WindowSource(url)
    return Cv2Source(kind, url, width, height)


def measure_fps(source, n_frames=100):
    """FPS thuc do sau n_frames khung — de bench 360P + log toc do khung."""
    t0 = time.time()
    count = 0
    while count < n_frames:
        ok, _ = source.read()
        if not ok:
            break
        count += 1
    dt = time.time() - t0
    return count / dt if dt > 0 else 0.0
