import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import datetime
import winsound
import threading

class StudyAlarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Alarm Scheduler")
        self.root.geometry("400x400")

        self.schedule = []  # List of (start, end) tuples
        self.alarm_thread = None
        self.running = False

        # UI Elements
        self.label = tk.Label(root, text="Study Schedule", font=("Arial", 16))
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(root, height=10, width=50)
        self.listbox.pack(pady=10)

        self.add_button = tk.Button(root, text="Add Study Period", command=self.add_period)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(root, text="Remove Selected", command=self.remove_period)
        self.remove_button.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Alarm", command=self.start_alarm, bg="green", fg="white")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Alarm", command=self.stop_alarm, bg="red", fg="white", state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.update_listbox()

    def add_period(self):
        start = simpledialog.askstring("Start Time", "Enter start time (HH:MM):", parent=self.root)
        if not start:
            return
        end = simpledialog.askstring("End Time", "Enter end time (HH:MM):", parent=self.root)
        if not end:
            return
        try:
            time.strptime(start, "%H:%M")
            time.strptime(end, "%H:%M")
            self.schedule.append((start, end))
            self.schedule.sort()  # Sort by start time
            self.update_listbox()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM.")

    def remove_period(self):
        selected = self.listbox.curselection()
        if selected:
            del self.schedule[selected[0]]
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for start, end in self.schedule:
            self.listbox.insert(tk.END, f"{start} - {end}")

    def start_alarm(self):
        if not self.schedule:
            messagebox.showerror("Error", "No study periods added.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")
        self.alarm_thread = threading.Thread(target=self.run_alarm)
        self.alarm_thread.start()

    def stop_alarm(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")
        if self.alarm_thread:
            self.alarm_thread.join()

    def run_alarm(self):
        while self.running:
            now = datetime.datetime.now()
            current_seconds = now.hour * 3600 + now.minute * 60 + now.second
            next_start = None
            next_end = None
            in_study = False
            for start, end in self.schedule:
                start_sec = self.time_to_seconds(start)
                end_sec = self.time_to_seconds(end)
                if current_seconds < start_sec:
                    if next_start is None or start_sec < next_start:
                        next_start = start_sec
                        next_end = end_sec
                elif current_seconds < end_sec:
                    in_study = True
                    self.root.after(0, lambda: self.status_label.config(text=f"Status: Studying until {end}"))
                    time.sleep(end_sec - current_seconds)
                    if self.running:
                        self.root.after(0, lambda: self.status_label.config(text="Status: Study time end!"))
                        winsound.Beep(1000, 1000)
                        self.root.after(0, lambda: self.status_label.config(text="Status: Running"))
                    break
            if not in_study:
                if next_start:
                    self.root.after(0, lambda: self.status_label.config(text=f"Status: Next study at {self.seconds_to_time(next_start)}"))
                    sleep_time = next_start - current_seconds
                    if sleep_time > 0:
                        time.sleep(min(sleep_time, 60))  # Check every minute
                    if self.running:
                        self.root.after(0, lambda: self.status_label.config(text="Status: Study time start!"))
                        winsound.Beep(1000, 1000)
                        end_sleep = next_end - (next_start + 1)
                        if end_sleep > 0:
                            time.sleep(end_sleep)
                        if self.running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Study time end!"))
                            winsound.Beep(1000, 1000)
                            self.root.after(0, lambda: self.status_label.config(text="Status: Running"))
                else:
                    # No more today
                    if self.schedule:
                        tomorrow_start = self.time_to_seconds(self.schedule[0][0]) + 24 * 3600
                        sleep_time = tomorrow_start - current_seconds
                        self.root.after(0, lambda: self.status_label.config(text=f"Status: Sleeping until tomorrow {self.schedule[0][0]}"))
                        time.sleep(min(sleep_time, 3600))  # Check every hour
            time.sleep(1)  # Prevent tight loop

    def time_to_seconds(self, t):
        h, m = map(int, t.split(':'))
        return h * 3600 + m * 60

    def seconds_to_time(self, s):
        h = s // 3600
        m = (s % 3600) // 60
        return f"{h:02d}:{m:02d}"

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyAlarmApp(root)
    root.mainloop()