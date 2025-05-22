import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from copy import deepcopy

class SchedulixSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Schedulix - Ultimate OS Scheduler")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f111a")

        self.processes = []
        self.selected_algorithm = tk.StringVar(value="FCFS")
        self.quantum = tk.IntVar(value=4)
        self.metrics = []
        self.simulation_running = False
        self.algorithm_results = {}
        self.build_ui()

    def build_ui(self):
        title = tk.Label(self.root, text="Schedulix - OS Scheduling Simulator", font=("Orbitron", 22, "bold"), fg="#00f5d4", bg="#0f111a")
        title.pack(pady=10)

        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        ttk.Label(frame, text="PID").grid(row=0, column=0)
        ttk.Label(frame, text="Arrival").grid(row=0, column=1)
        ttk.Label(frame, text="Burst").grid(row=0, column=2)
        ttk.Label(frame, text="Priority").grid(row=0, column=3)

        self.pid_entry = ttk.Entry(frame, width=5)
        self.pid_entry.grid(row=1, column=0)

        self.arrival_entry = ttk.Entry(frame, width=10)
        self.arrival_entry.grid(row=1, column=1)

        self.burst_entry = ttk.Entry(frame, width=10)
        self.burst_entry.grid(row=1, column=2)

        self.priority_entry = ttk.Entry(frame, width=10)
        self.priority_entry.grid(row=1, column=3)

        ttk.Button(frame, text="Add", command=self.add_process).grid(row=1, column=4, padx=5)
        ttk.Button(frame, text="Start Simulation", command=self.start_simulation).grid(row=1, column=5, padx=5)
        ttk.Button(frame, text="Reset", command=self.reset).grid(row=1, column=6)

        ttk.Label(frame, text="Algorithm:").grid(row=1, column=7, padx=10)
        algo_menu = ttk.OptionMenu(frame, self.selected_algorithm, "FCFS", "FCFS", "SJF (Non-preemptive)", "SJF (Preemptive)", "Priority", "Round Robin")
        algo_menu.grid(row=1, column=8)

        ttk.Label(frame, text="Quantum:").grid(row=1, column=9)
        ttk.Entry(frame, textvariable=self.quantum, width=5).grid(row=1, column=10)

        self.canvas = tk.Canvas(self.root, bg="#1a1c29", height=250, width=1150, highlightthickness=0)
        self.canvas.pack(pady=15)
        self.timeline = self.canvas.create_line(0, 125, 0, 125, fill="#00ffcc", width=4)

        # Add time markers
        self.time_labels = []

        self.metrics_table = ttk.Treeview(self.root, columns=("PID", "Arrival", "Burst", "CT", "TAT", "WT", "RT"), show="headings", height=6)
        for col in self.metrics_table["columns"]:
            self.metrics_table.heading(col, text=col)
            self.metrics_table.column(col, anchor="center", width=100)
        self.metrics_table.pack(pady=10)

        self.summary_label = tk.Label(self.root, text="", fg="white", bg="#0f111a", font=("Helvetica", 10, "bold"))
        self.summary_label.pack(pady=5)

        self.log_output = tk.Text(self.root, height=6, width=140, bg="#0e0f1c", fg="#00ffcc", font=("Consolas", 10))
        self.log_output.pack(pady=5)

        # Add comparison button
        ttk.Button(self.root, text="Compare All Algorithms", command=self.compare_all_algorithms).pack(pady=5)

    def add_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get()) if self.priority_entry.get() else 0
            
            # Check for existing PID
            if any(p["pid"] == pid for p in self.processes):
                messagebox.showerror("Duplicate PID", f"Process with PID {pid} already exists.")
                return
                
            self.processes.append({"pid": pid, "arrival": arrival, "burst": burst, "priority": priority, "remaining": burst})
            self.log_output.insert(tk.END, f"Added Process - PID: {pid}, Arrival: {arrival}, Burst: {burst}, Priority: {priority}\n")
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid numbers only.")

    def reset(self):
        if self.simulation_running:
            messagebox.showinfo("Simulation Running", "Please wait for simulation to complete before resetting.")
            return
            
        self.processes.clear()
        self.metrics.clear()
        self.algorithm_results.clear()
        self.canvas.delete("all")
        self.timeline = self.canvas.create_line(0, 125, 0, 125, fill="#00ffcc", width=4)
        
        # Clear time labels
        for label in self.time_labels:
            self.canvas.delete(label)
        self.time_labels.clear()
        
        self.metrics_table.delete(*self.metrics_table.get_children())
        self.summary_label.config(text="")
        self.log_output.delete("1.0", tk.END)
        
        # Remove graph if exists
        for widget in self.root.pack_slaves():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

    def start_simulation(self):
        if not self.processes:
            messagebox.showwarning("No Data", "Please add processes before starting.")
            return
            
        if self.simulation_running:
            messagebox.showinfo("Simulation Running", "A simulation is already in progress.")
            return
            
        # Clear previous results
        self.canvas.delete("all")
        self.timeline = self.canvas.create_line(0, 125, 0, 125, fill="#00ffcc", width=4)
        for label in self.time_labels:
            self.canvas.delete(label)
        self.time_labels.clear()
        self.metrics_table.delete(*self.metrics_table.get_children())
        
        # Create deep copy of processes to prevent modifying original data
        processes_copy = deepcopy(self.processes)
        
        algorithm = self.selected_algorithm.get()
        
        # Start appropriate algorithm in a thread
        self.simulation_running = True
        thread = threading.Thread(target=self.run_algorithm, args=(algorithm, processes_copy))
        thread.start()

    def run_algorithm(self, algorithm, processes):
        try:
            if algorithm == "FCFS":
                self.run_fcfs(processes)
            elif algorithm == "SJF (Non-preemptive)":
                self.run_sjf_non_preemptive(processes)
            elif algorithm == "SJF (Preemptive)":
                self.run_sjf_preemptive(processes)
            elif algorithm == "Priority":
                self.run_priority(processes)
            elif algorithm == "Round Robin":
                self.run_round_robin(processes)
        finally:
            self.simulation_running = False

    def run_fcfs(self, processes):
        time_unit = 30
        processes.sort(key=lambda x: x["arrival"])
        current_time = 0
        x_start = 10
        y_pos = 100
        colors = ["#ff6b6b", "#6bc1ff", "#51ff90", "#ffc75f", "#c26bff", "#f06595", "#f2a154"]
        self.metrics = []
        
        for i, p in enumerate(processes):
            pid = p["pid"]
            at = p["arrival"]
            bt = p["burst"]
            color = colors[i % len(colors)]
            
            if at > current_time:
                idle_time = at - current_time
                self.draw_bar("IDLE", current_time, idle_time, x_start, y_pos, "#44475a", time_unit)
                x_start += idle_time * time_unit
                current_time = at

            start_time = current_time
            self.draw_bar(f"P{pid}", current_time, bt, x_start, y_pos, color, time_unit)
            completion_time = current_time + bt
            tat = completion_time - at
            wt = tat - bt
            rt = start_time - at
            self.metrics.append((pid, at, bt, completion_time, tat, wt, rt))
            x_start += bt * time_unit
            current_time += bt
            
        self.draw_time_markers(time_unit)
        self.show_metrics("FCFS")

    def run_sjf_non_preemptive(self, processes):
        time_unit = 30
        processes.sort(key=lambda x: x["arrival"])
        current_time = 0
        x_start = 10
        y_pos = 100
        colors = ["#ff6b6b", "#6bc1ff", "#51ff90", "#ffc75f", "#c26bff", "#f06595", "#f2a154"]
        self.metrics = []
        
        # Make a copy to track completion
        remaining_processes = deepcopy(processes)
        color_map = {p["pid"]: colors[i % len(colors)] for i, p in enumerate(processes)}
        
        while remaining_processes:
            # Find ready processes
            ready_processes = [p for p in remaining_processes if p["arrival"] <= current_time]
            
            if not ready_processes:
                # No process available, idle CPU
                next_process = min(remaining_processes, key=lambda x: x["arrival"])
                idle_time = next_process["arrival"] - current_time
                self.draw_bar("IDLE", current_time, idle_time, x_start, y_pos, "#44475a", time_unit)
                x_start += idle_time * time_unit
                current_time = next_process["arrival"]
                continue
                
            # Find shortest job
            next_process = min(ready_processes, key=lambda x: x["burst"])
            pid = next_process["pid"]
            at = next_process["arrival"]
            bt = next_process["burst"]
            color = color_map[pid]
            
            # Execute process
            start_time = current_time
            self.draw_bar(f"P{pid}", current_time, bt, x_start, y_pos, color, time_unit)
            completion_time = current_time + bt
            tat = completion_time - at
            wt = tat - bt
            rt = start_time - at
            self.metrics.append((pid, at, bt, completion_time, tat, wt, rt))
            
            # Update time and x_start
            x_start += bt * time_unit
            current_time += bt
            
            # Remove completed process
            remaining_processes = [p for p in remaining_processes if p["pid"] != pid]
            
        self.draw_time_markers(time_unit)
        self.show_metrics("SJF (Non-preemptive)")

    def run_sjf_preemptive(self, processes):
        time_unit = 30
        processes.sort(key=lambda x: x["arrival"])
        current_time = 0
        x_start = 10
        y_pos = 100
        colors = ["#ff6b6b", "#6bc1ff", "#51ff90", "#ffc75f", "#c26bff", "#f06595", "#f2a154"]
        self.metrics = []
        
        # Make a copy to track completion and start times
        remaining_processes = deepcopy(processes)
        color_map = {p["pid"]: colors[i % len(colors)] for i, p in enumerate(processes)}
        response_times = {}  # Track first time a process gets CPU
        start_times = {}     # Track when a process starts execution
        
        # Find all unique arrival times and completion possibilities
        events = set()
        for p in processes:
            events.add(p["arrival"])
        
        # Add events when processes might complete
        while remaining_processes:
            ready_processes = [p for p in remaining_processes if p["arrival"] <= current_time]
            
            if not ready_processes:
                # No process available, idle until next arrival
                next_arrival = min([p["arrival"] for p in remaining_processes])
                idle_time = next_arrival - current_time
                self.draw_bar("IDLE", current_time, idle_time, x_start, y_pos, "#44475a", time_unit)
                x_start += idle_time * time_unit
                current_time = next_arrival
                continue
                
            # Find shortest remaining time process
            next_process = min(ready_processes, key=lambda x: x["remaining"])
            pid = next_process["pid"]
            
            # Calculate how long until next event (new process arrival or current process completion)
            next_event_time = float('inf')
            for p in remaining_processes:
                if p["arrival"] > current_time and p["arrival"] < next_event_time:
                    next_event_time = p["arrival"]
            
            # Process could complete before next arrival
            time_slice = min(next_process["remaining"], 
                             next_event_time - current_time if next_event_time != float('inf') else next_process["remaining"])
            
            # Track response time the first time a process gets CPU
            if pid not in response_times:
                response_times[pid] = current_time - next_process["arrival"]
            
            # Execute the process for the time slice
            color = color_map[pid]
            self.draw_bar(f"P{pid}", current_time, time_slice, x_start, y_pos, color, time_unit)
            
            # Update time and x_start
            x_start += time_slice * time_unit
            current_time += time_slice
            
            # Update remaining time for the process
            next_process["remaining"] -= time_slice
            
            # If process is complete, remove it
            if next_process["remaining"] <= 0:
                # Record metrics
                completion_time = current_time
                arrival_time = next_process["arrival"]
                burst_time = next_process["burst"]
                tat = completion_time - arrival_time
                wt = tat - burst_time
                rt = response_times[pid]
                self.metrics.append((pid, arrival_time, burst_time, completion_time, tat, wt, rt))
                
                # Remove from remaining processes
                remaining_processes = [p for p in remaining_processes if p["pid"] != pid]
        
        self.draw_time_markers(time_unit)
        self.show_metrics("SJF (Preemptive)")

    def run_priority(self, processes):
        time_unit = 30
        processes.sort(key=lambda x: x["arrival"])
        current_time = 0
        x_start = 10
        y_pos = 100
        colors = ["#ff6b6b", "#6bc1ff", "#51ff90", "#ffc75f", "#c26bff", "#f06595", "#f2a154"]
        self.metrics = []
        
        # Make a copy to track completion
        remaining_processes = deepcopy(processes)
        color_map = {p["pid"]: colors[i % len(colors)] for i, p in enumerate(processes)}
        response_times = {}  # Track first time a process gets CPU
        
        while remaining_processes:
            # Find ready processes
            ready_processes = [p for p in remaining_processes if p["arrival"] <= current_time]
            
            if not ready_processes:
                # No process available, idle CPU
                next_process = min(remaining_processes, key=lambda x: x["arrival"])
                idle_time = next_process["arrival"] - current_time
                self.draw_bar("IDLE", current_time, idle_time, x_start, y_pos, "#44475a", time_unit)
                x_start += idle_time * time_unit
                current_time = next_process["arrival"]
                continue
                
            # Find highest priority process (lower number = higher priority)
            next_process = min(ready_processes, key=lambda x: x["priority"])
            pid = next_process["pid"]
            at = next_process["arrival"]
            bt = next_process["burst"]
            color = color_map[pid]
            
            # Track response time
            if pid not in response_times:
                response_times[pid] = current_time - at
            
            # Execute process
            self.draw_bar(f"P{pid}", current_time, bt, x_start, y_pos, color, time_unit)
            completion_time = current_time + bt
            tat = completion_time - at
            wt = tat - bt
            rt = response_times[pid]
            self.metrics.append((pid, at, bt, completion_time, tat, wt, rt))
            
            # Update time and x_start
            x_start += bt * time_unit
            current_time += bt
            
            # Remove completed process
            remaining_processes = [p for p in remaining_processes if p["pid"] != pid]
            
        self.draw_time_markers(time_unit)
        self.show_metrics("Priority")

    def run_round_robin(self, processes):
        time_unit = 30
        processes.sort(key=lambda x: x["arrival"])
        current_time = 0
        x_start = 10
        y_pos = 100
        colors = ["#ff6b6b", "#6bc1ff", "#51ff90", "#ffc75f", "#c26bff", "#f06595", "#f2a154"]
        self.metrics = []
        quantum = self.quantum.get()
        
        # Make a copy to track completion
        remaining_processes = deepcopy(processes)
        color_map = {p["pid"]: colors[i % len(colors)] for i, p in enumerate(processes)}
        response_times = {}  # Track first time a process gets CPU
        completion_records = {p["pid"]: {"completion": 0, "first_response": -1} for p in processes}
        
        # Queue for ready processes
        ready_queue = []
        
        while remaining_processes or ready_queue:
            # Check if any new processes have arrived
            new_arrivals = [p for p in remaining_processes if p["arrival"] <= current_time]
            for p in new_arrivals:
                ready_queue.append(p)
                remaining_processes.remove(p)
            
            if not ready_queue:
                # No process in ready queue, idle CPU until next arrival
                if remaining_processes:
                    next_arrival = min([p["arrival"] for p in remaining_processes])
                    idle_time = next_arrival - current_time
                    self.draw_bar("IDLE", current_time, idle_time, x_start, y_pos, "#44475a", time_unit)
                    x_start += idle_time * time_unit
                    current_time = next_arrival
                    continue
                else:
                    break  # No more processes to execute
            
            # Get next process from ready queue
            current_process = ready_queue.pop(0)
            pid = current_process["pid"]
            
            # Track response time (first time getting CPU)
            if completion_records[pid]["first_response"] == -1:
                completion_records[pid]["first_response"] = current_time - current_process["arrival"]
            
            # Calculate time slice (minimum of quantum and remaining burst)
            time_slice = min(quantum, current_process["remaining"])
            
            # Execute the process for the time slice
            color = color_map[pid]
            self.draw_bar(f"P{pid}", current_time, time_slice, x_start, y_pos, color, time_unit)
            
            # Update time and x_start
            x_start += time_slice * time_unit
            current_time += time_slice
            
            # Update remaining time for the process
            current_process["remaining"] -= time_slice
            
            # Check for new arrivals during this execution
            new_arrivals = [p for p in remaining_processes if p["arrival"] <= current_time]
            for p in new_arrivals:
                ready_queue.append(p)
                remaining_processes.remove(p)
            
            # If process is not complete, put it back in the ready queue
            if current_process["remaining"] > 0:
                ready_queue.append(current_process)
            else:
                # Record completion metrics
                completion_time = current_time
                arrival_time = current_process["arrival"]
                burst_time = current_process["burst"]
                tat = completion_time - arrival_time
                wt = tat - burst_time
                rt = completion_records[pid]["first_response"]
                self.metrics.append((pid, arrival_time, burst_time, completion_time, tat, wt, rt))
                completion_records[pid]["completion"] = completion_time
        
        self.draw_time_markers(time_unit)
        self.show_metrics("Round Robin")

    def draw_bar(self, label, start, duration, x_start, y_pos, color, unit):
        for t in range(duration):
            rect = self.canvas.create_rectangle(
                x_start + t * unit, y_pos,
                x_start + (t + 1) * unit, y_pos + 50,
                fill=color, outline="white", width=2
            )
            self.canvas.create_text(
                x_start + t * unit + unit // 2, y_pos + 25,
                text=label if t == duration // 2 else "",
                fill="white", font=("Helvetica", 10, "bold")
            )
            self.canvas.update()
            self.canvas.coords(self.timeline, 0, 125, x_start + (t + 1) * unit, 125)
            time.sleep(0.1)  # Slightly faster animation

        self.log_output.insert(tk.END, f"{label} executed from time {start} to {start + duration}\n")
        self.log_output.see(tk.END)
    
    def draw_time_markers(self, time_unit):
        # Clear previous time markers
        for label in self.time_labels:
            self.canvas.delete(label)
        self.time_labels.clear()
        
        # Get canvas width
        canvas_width = self.canvas.winfo_width()
        
        # Calculate maximum time that fits on canvas
        max_time = int((canvas_width - 10) / time_unit)
        
        # Draw time markers every 5 units
        for t in range(0, max_time + 1, 5):
            x_pos = 10 + t * time_unit
            # Draw marker line
            line = self.canvas.create_line(x_pos, 85, x_pos, 95, fill="white", width=2)
            self.time_labels.append(line)
            # Draw time label
            text = self.canvas.create_text(x_pos, 75, text=str(t), fill="white", font=("Helvetica", 8))
            self.time_labels.append(text)

    def show_metrics(self, algorithm_name):
        self.metrics_table.delete(*self.metrics_table.get_children())
        for metric in self.metrics:
            self.metrics_table.insert("", tk.END, values=metric)

        n = len(self.metrics)
        avg_tat = sum(m[4] for m in self.metrics) / n if n > 0 else 0
        avg_wt = sum(m[5] for m in self.metrics) / n if n > 0 else 0
        avg_rt = sum(m[6] for m in self.metrics) / n if n > 0 else 0
        total_time = max(m[3] for m in self.metrics) if n > 0 else 0
        throughput = n / total_time if total_time > 0 else 0

        summary = f"{algorithm_name} | Avg TAT: {avg_tat:.2f} | Avg WT: {avg_wt:.2f} | Avg RT: {avg_rt:.2f} | Throughput: {throughput:.2f} processes/unit"
        self.summary_label.config(text=summary)

        # Store results for comparison
        self.algorithm_results[algorithm_name] = {
            "TAT": avg_tat,
            "WT": avg_wt,
            "RT": avg_rt,
            "Throughput": throughput
        }
        
        self.draw_algorithm_graph(algorithm_name)

    def draw_algorithm_graph(self, algorithm_name):
        # Create a popup window for the algorithm graph
        popup = tk.Toplevel(self.root)
        popup.title(f"{algorithm_name} Performance")
        popup.geometry("600x500")
        popup.configure(bg="#0f111a")
        
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        metrics = ["TAT", "WT", "RT", "Throughput"]
        values = [
            self.algorithm_results[algorithm_name]["TAT"],
            self.algorithm_results[algorithm_name]["WT"],
            self.algorithm_results[algorithm_name]["RT"],
            self.algorithm_results[algorithm_name]["Throughput"]
        ]
        
        bars = ax.bar(metrics, values, color=["#4caf50", "#2196f3", "#ff9800", "#9c27b0"])
        ax.set_title(f"{algorithm_name} Performance", fontsize=14)
        ax.set_ylabel("Units", fontsize=12)
        
        # Add value labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9)

        # Create the canvas in the popup window
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add a close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def compare_all_algorithms(self):
        if not self.processes:
            messagebox.showwarning("No Data", "Please add processes before comparing.")
            return
            
        if self.simulation_running:
            messagebox.showinfo("Simulation Running", "Please wait for current simulation to complete.")
            return
            
        if len(self.algorithm_results) < 2:
            messagebox.showinfo("Insufficient Data", "Run at least two different algorithms to compare.")
            return
            
        # Create a popup window for the comparison graph
        popup = tk.Toplevel(self.root)
        popup.title("Algorithm Comparison")
        popup.geometry("800x600")
        popup.configure(bg="#0f111a")
        
        # Create the figure with larger size
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        algorithms = list(self.algorithm_results.keys())
        metrics = ["TAT", "WT", "RT", "Throughput"]
        
        x = np.arange(len(metrics))
        width = 0.8 / len(algorithms)
        
        for i, algo in enumerate(algorithms):
            values = [
                self.algorithm_results[algo]["TAT"],
                self.algorithm_results[algo]["WT"],
                self.algorithm_results[algo]["RT"],
                self.algorithm_results[algo]["Throughput"]
            ]
            offset = width * i - width * (len(algorithms) - 1) / 2
            ax.bar(x + offset, values, width, label=algo)
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Values', fontsize=12)
        ax.set_title('Algorithm Comparison', fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=10)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        # Create the canvas in the popup window
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add a close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

if __name__ == "__main__":
    # Fix missing numpy import
    import numpy as np
    
    root = tk.Tk()
    app = SchedulixSimulator(root)
    root.mainloop()