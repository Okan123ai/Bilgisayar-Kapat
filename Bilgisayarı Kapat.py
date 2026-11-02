import ctypes
import subprocess
import sys
import tkinter as tk
from ctypes import wintypes
from tkinter import messagebox, ttk


def run_power_action(action: str) -> None:
    if sys.platform != "win32":
        messagebox.showerror(
            "Desteklenmiyor",
            "Bu uygulama yalnızca Windows'ta çalışır.",
        )
        return

    actions = {
        "kapat": ("Bilgisayarı kapatmak", ["/s", "/t", "0"]),
        "yeniden başlat": ("Bilgisayarı yeniden başlatmak", ["/r", "/t", "0"]),
    }
    description = action.capitalize()
    if action in actions:
        description, arguments = actions[action]
        if not messagebox.askyesno(
            "Onay gerekiyor",
            f"{description} istediğinizden emin misiniz?",
        ):
            return
        try:
            subprocess.run(
                ["shutdown", *arguments],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            messagebox.showerror("İşlem başarısız", f"{description} işlemi başlatılamadı:\n{error}")
        return

    if action not in ("uyku", "hazırda beklet"):
        messagebox.showerror("Hata", "Bilinmeyen güç seçeneği.")
        return

    if not messagebox.askyesno(
        "Onay gerekiyor",
        f"Bilgisayarı {action} moduna almak istediğinizden emin misiniz?",
    ):
        return

    try:
        powrprof = ctypes.WinDLL("PowrProf.dll", use_last_error=True)
        set_suspend_state = powrprof.SetSuspendState
        set_suspend_state.argtypes = (wintypes.BOOLEAN, wintypes.BOOLEAN, wintypes.BOOLEAN)
        set_suspend_state.restype = wintypes.BOOLEAN
        hibernate = action == "hazırda beklet"
        if not set_suspend_state(hibernate, False, False):
            error_code = ctypes.get_last_error()
            messagebox.showerror(
                "İşlem başarısız",
                f"{description} işlemi başlatılamadı (Windows hata kodu: {error_code}).",
            )
    except (AttributeError, OSError) as error:
        messagebox.showerror("İşlem başarısız", f"{description} işlemi başlatılamadı:\n{error}")


def main() -> None:
    root = tk.Tk()
    root.title("Bilgisayar Güç Seçenekleri")
    root.resizable(False, False)
    root.configure(bg="#f3f5f8")

    style = ttk.Style(root)
    style.configure("Title.TLabel", background="#f3f5f8", foreground="#172033", font=("Segoe UI", 18, "bold"))
    style.configure("Info.TLabel", background="#f3f5f8", foreground="#5c667a", font=("Segoe UI", 10))
    style.configure("Power.TButton", font=("Segoe UI", 11), padding=(12, 10))

    content = ttk.Frame(root, padding=24)
    content.pack(fill="both", expand=True)
    ttk.Label(content, text="Güç seçenekleri", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        content,
        text="Bir işlem seçin. Devam etmeden önce onayınız istenir.",
        style="Info.TLabel",
        wraplength=330,
    ).pack(anchor="w", pady=(6, 18))

    buttons = (
        ("Bilgisayarı kapat", "kapat"),
        ("Yeniden başlat", "yeniden başlat"),
        ("Uyku modu", "uyku"),
        ("Hazırda beklet", "hazırda beklet"),
    )
    for label, action in buttons:
        ttk.Button(
            content,
            text=label,
            style="Power.TButton",
            command=lambda selected_action=action: run_power_action(selected_action),
        ).pack(fill="x", pady=4)

    root.mainloop()


if __name__ == "__main__":
    main()