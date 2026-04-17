import tkinter as tk
from tkinter import ttk, messagebox

# ================= PROCESS =================
class Process:
    def __init__(self, pid, burst, priority=0):
        self.pid = pid
        self.burst = burst
        self.remaining = burst
        self.priority = priority
        self.state = "Ready"

# ================= MAIN APP =================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduler Simulator")
        self.root.geometry("700x500")
        self.root.configure(bg="#f4f6f7")
        self.show_setup()

    def show_setup(self):
        self.running = False
        self.clear()

        container = tk.Frame(self.root, bg="#f4f6f7")
        container.pack(pady=20)

        tk.Label(container, text="Scheduler Setup",
                 font=("Arial", 18, "bold"),
                 bg="#f4f6f7").pack(pady=10)

        self.algo = tk.StringVar(value="FCFS")

        self.algo_box = ttk.Combobox(container,
                                     textvariable=self.algo,
                                     values=["FCFS", "SJF", "Round Robin"],
                                     state="readonly")
        self.algo_box.pack(pady=5)
        self.algo_box.bind("<<ComboboxSelected>>", self.toggle_options)

        self.use_priority = tk.BooleanVar()
        self.priority_check = tk.Checkbutton(
            container,
            text="Enable Priority Scheduling",
            variable=self.use_priority,
            bg="#f4f6f7"
        )
        self.priority_check.pack()

        self.tq_label = tk.Label(container, text="Time Quantum", bg="#f4f6f7")
        self.tq_entry = tk.Entry(container)

        tk.Button(container, text="Proceed",
                  bg="#3498db", fg="white",
                  command=self.start_simulator).pack(pady=15)

    def toggle_options(self, event=None):
        if self.algo.get() == "Round Robin":
            self.tq_label.pack()
            self.tq_entry.pack()
            self.priority_check.pack_forget()
            self.use_priority.set(False)
        else:
            self.tq_label.pack_forget()
            self.tq_entry.pack_forget()
            self.priority_check.pack()

    def start_simulator(self):
        self.algorithm = self.algo.get()
        self.priority_mode = self.use_priority.get()

        if self.algorithm == "Round Robin":
            if not self.tq_entry.get():
                messagebox.showerror("Error", "Enter Time Quantum")
                return
            self.time_quantum = int(self.tq_entry.get())

        self.clear()
        self.build_simulator()

    def build_simulator(self):
        self.processes = []
        self.queue = []
        self.current = None
        self.counter = 0
        self.running = False

        top = tk.Frame(self.root, bg="#ecf0f1")
        top.pack(fill="x")

        tk.Label(top, text=f"Algorithm: {self.algorithm}",
                 font=("Arial", 12, "bold"),
                 bg="#ecf0f1").pack(side="left", padx=10)

        tk.Button(top, text="Back",
                  command=self.show_setup).pack(side="right", padx=10)

        frame = tk.LabelFrame(self.root, text="Add Process",
                              padx=10, pady=10, bg="#f4f6f7")
        frame.pack(pady=10)

        tk.Label(frame, text="PID", bg="#f4f6f7").grid(row=0, column=0)
        self.pid = tk.Entry(frame)
        self.pid.grid(row=0, column=1)

        tk.Label(frame, text="Burst Time", bg="#f4f6f7").grid(row=1, column=0)
        self.burst = tk.Entry(frame)
        self.burst.grid(row=1, column=1)

        if self.priority_mode:
            tk.Label(frame, text="Priority", bg="#f4f6f7").grid(row=2, column=0)
            self.priority = tk.Entry(frame)
            self.priority.grid(row=2, column=1)

        tk.Button(frame, text="Add Process",
                  bg="#2ecc71", fg="white",
                  command=self.add_process).grid(row=3, columnspan=2, pady=5)

        self.tree = ttk.Treeview(self.root,
            columns=("PID","Burst","Remain","Priority","State"),
            show="headings")

        for col in ("PID","Burst","Remain","Priority","State"):
            self.tree.heading(col, text=col)

        self.tree.pack(pady=10)

        btn = tk.Frame(self.root, bg="#f4f6f7")
        btn.pack()

        tk.Button(btn, text="Next Step",
                  bg="#3498db", fg="white",
                  command=self.next_step).grid(row=0, column=0, padx=5)

        tk.Button(btn, text="Start",
                  bg="#2ecc71", fg="white",
                  command=self.start_auto).grid(row=0, column=1, padx=5)

        tk.Button(btn, text="Stop",
                  bg="#e74c3c", fg="white",
                  command=self.stop_auto).grid(row=0, column=2, padx=5)

    def add_process(self):
        pid = self.pid.get()
        burst = self.burst.get()

        if not pid or not burst:
            messagebox.showerror("Error", "Fill all fields")
            return

        if any(p.pid == pid for p in self.processes):
            messagebox.showerror("Error", "Duplicate PID")
            return

        pr = int(self.priority.get()) if self.priority_mode else 0

        p = Process(pid, int(burst), pr)
        self.processes.append(p)
        self.queue.append(p)

        self.update_table()

    def pick_process(self):
        if self.priority_mode:
            self.queue.sort(key=lambda x: x.priority)

        if self.algorithm == "SJF":
            self.queue.sort(key=lambda x: x.remaining)

        return self.queue.pop(0)

    def next_step(self):
        if self.current is None and self.queue:
            self.current = self.pick_process()
            self.counter = 0

        if self.current:
            self.current.remaining -= 1
            self.counter += 1

            if self.current.remaining == 0:
                self.current.state = "Terminated"
                self.current = None

            elif self.algorithm == "Round Robin" and self.counter == self.time_quantum:
                self.current.state = "Ready"
                self.queue.append(self.current)
                self.current = None

        self.update_table()

    def start_auto(self):
        self.running = True
        self.run_auto()

    def run_auto(self):
        if self.running:
            self.next_step()
            self.root.after(800, self.run_auto)

    def stop_auto(self):
        self.running = False

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in self.processes:
            self.tree.insert("", "end",
                values=(p.pid, p.burst, p.remaining, p.priority, p.state))

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ================= RUN =================
root = tk.Tk()
app = App(root)
root.mainloop()
