import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithm Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        self.processes = []
        self.results = []
        self.animation_running = False
        self.animation_paused = False
        self.current_time = 0
        self.animation_speed = 500  # milliseconds per time unit
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', pady=10)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="CPU SCHEDULING ALGORITHM SIMULATOR", 
                font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white').pack()
        
        # Create main container with scrollbar
        container = tk.Frame(self.root, bg='#f0f0f0')
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(container, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main container
        main_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input
        left_frame = tk.LabelFrame(main_frame, text="Process Input", 
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Process ID
        tk.Label(left_frame, text="Process ID:", bg='#ecf0f1', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.pid_entry = tk.Entry(left_frame, width=15, font=('Arial', 10))
        self.pid_entry.grid(row=0, column=1, pady=5)
        
        # Arrival Time
        tk.Label(left_frame, text="Arrival Time:", bg='#ecf0f1', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.arrival_entry = tk.Entry(left_frame, width=15, font=('Arial', 10))
        self.arrival_entry.grid(row=1, column=1, pady=5)
        
        # Burst Time
        tk.Label(left_frame, text="Burst Time:", bg='#ecf0f1', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.burst_entry = tk.Entry(left_frame, width=15, font=('Arial', 10))
        self.burst_entry.grid(row=2, column=1, pady=5)
        
        # Priority
        tk.Label(left_frame, text="Priority (lower=higher):", bg='#ecf0f1', font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
        self.priority_entry = tk.Entry(left_frame, width=15, font=('Arial', 10))
        self.priority_entry.grid(row=3, column=1, pady=5)
        self.priority_entry.insert(0, "0")
        
        # Buttons
        button_frame = tk.Frame(left_frame, bg='#ecf0f1')
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Add Process", command=self.add_process, 
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_all, 
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Process List
        list_frame = tk.Frame(left_frame, bg='#ecf0f1')
        list_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='nsew')
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.process_listbox = tk.Listbox(list_frame, height=10, width=35, 
                                          font=('Courier', 9), yscrollcommand=scrollbar.set)
        self.process_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_listbox.yview)
        
        # Algorithm Selection
        algo_frame = tk.LabelFrame(left_frame, text="Select Algorithm", 
                                   font=('Arial', 11, 'bold'), bg='#ecf0f1', pady=10)
        algo_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.algorithm_var = tk.StringVar(value="FCFS")
        algorithms = [("FCFS", "FCFS"), ("SJF", "SJF"), ("Priority", "Priority"), ("Round Robin", "RR")]
        
        for i, (text, value) in enumerate(algorithms):
            tk.Radiobutton(algo_frame, text=text, variable=self.algorithm_var, 
                          value=value, bg='#ecf0f1', font=('Arial', 10),
                          command=self.toggle_quantum).grid(row=i//2, column=i%2, sticky='w', padx=10)
        
        # Quantum for Round Robin
        self.quantum_frame = tk.Frame(algo_frame, bg='#ecf0f1')
        self.quantum_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tk.Label(self.quantum_frame, text="Time Quantum:", bg='#ecf0f1', font=('Arial', 10)).pack(side=tk.LEFT)
        self.quantum_entry = tk.Entry(self.quantum_frame, width=10, font=('Arial', 10))
        self.quantum_entry.pack(side=tk.LEFT, padx=5)
        self.quantum_entry.insert(0, "2")
        self.quantum_frame.grid_remove()
        
        # Execute Button
        execute_frame = tk.Frame(left_frame, bg='#ecf0f1')
        execute_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        tk.Button(execute_frame, text="▶ EXECUTE", command=self.execute_scheduling,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=12, height=2, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(execute_frame, text="🎬 ANIMATE", command=self.start_animation,
                 bg='#9b59b6', fg='white', font=('Arial', 11, 'bold'),
                 width=12, height=2, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Animation Controls
        control_frame = tk.Frame(left_frame, bg='#ecf0f1')
        control_frame.grid(row=8, column=0, columnspan=2, pady=5)
        
        self.pause_btn = tk.Button(control_frame, text="⏸ Pause", command=self.toggle_pause,
                 bg='#f39c12', fg='white', font=('Arial', 9, 'bold'),
                 width=8, cursor='hand2', state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=3)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Stop", command=self.stop_animation,
                 bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'),
                 width=8, cursor='hand2', state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
        
        # Speed Control
        speed_frame = tk.Frame(left_frame, bg='#ecf0f1')
        speed_frame.grid(row=9, column=0, columnspan=2, pady=5)
        tk.Label(speed_frame, text="Speed:", bg='#ecf0f1', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        self.speed_scale = tk.Scale(speed_frame, from_=100, to=2000, orient=tk.HORIZONTAL,
                                    length=150, command=self.update_speed, bg='#ecf0f1')
        self.speed_scale.set(500)
        self.speed_scale.pack(side=tk.LEFT)
        tk.Label(speed_frame, text="ms", bg='#ecf0f1', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Right panel - Results
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Gantt Chart
        gantt_frame = tk.LabelFrame(right_frame, text="Gantt Chart (Animation)", 
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', padx=5, pady=5)
        gantt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.figure = Figure(figsize=(9, 3), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.figure, master=gantt_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Current Time Display
        self.time_label = tk.Label(gantt_frame, text="Current Time: 0", 
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#e74c3c')
        self.time_label.pack(pady=5)
        
        # Process Status Display
        status_frame = tk.LabelFrame(right_frame, text="Process Status", 
                                     font=('Arial', 11, 'bold'), bg='#ecf0f1', padx=5, pady=5)
        status_frame.pack(fill=tk.BOTH, pady=5)
        
        self.status_text = tk.Text(status_frame, height=6, width=70, font=('Courier', 9),
                                   bg='#fffacd', relief=tk.SUNKEN, borderwidth=2)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = tk.LabelFrame(right_frame, text="Statistics", 
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=12, width=70, font=('Courier', 9),
                                 bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(5, weight=1)
    
    def toggle_quantum(self):
        if self.algorithm_var.get() == "RR":
            self.quantum_frame.grid()
        else:
            self.quantum_frame.grid_remove()
    
    def update_speed(self, val):
        self.animation_speed = int(val)
    
    def toggle_pause(self):
        self.animation_paused = not self.animation_paused
        if self.animation_paused:
            self.pause_btn.config(text="▶ Resume")
        else:
            self.pause_btn.config(text="⏸ Pause")
    
    def stop_animation(self):
        self.animation_running = False
        self.animation_paused = False
        self.pause_btn.config(state=tk.DISABLED, text="⏸ Pause")
        self.stop_btn.config(state=tk.DISABLED)
        self.current_time = 0
    
    def add_process(self):
        try:
            pid = self.pid_entry.get().strip()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())
            
            if not pid:
                messagebox.showwarning("Warning", "Please enter Process ID!")
                return
            
            if burst <= 0:
                messagebox.showwarning("Warning", "Burst time must be positive!")
                return
            
            process = Process(pid, arrival, burst, priority)
            self.processes.append(process)
            
            self.process_listbox.insert(tk.END, 
                f"{pid:5} | AT:{arrival:3} | BT:{burst:3} | P:{priority:2}")
            
            # Clear entries
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            self.priority_entry.insert(0, "0")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def clear_all(self):
        self.stop_animation()
        self.processes = []
        self.results = []
        self.process_listbox.delete(0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.status_text.delete(1.0, tk.END)
        self.time_label.config(text="Current Time: 0")
        self.figure.clear()
        self.canvas.draw()
    
    def start_animation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process!")
            return
        
        if self.animation_running:
            messagebox.showinfo("Info", "Animation is already running!")
            return
        
        algorithm = self.algorithm_var.get()
        
        # Calculate scheduling first
        if algorithm == "FCFS":
            self.fcfs_scheduling()
        elif algorithm == "SJF":
            self.sjf_scheduling()
        elif algorithm == "Priority":
            self.priority_scheduling()
        elif algorithm == "RR":
            try:
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    raise ValueError
                self.round_robin_scheduling(quantum)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid time quantum!")
                return
        
        # Start animation
        self.animation_running = True
        self.animation_paused = False
        self.current_time = 0
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.animate_scheduling()
    
    def animate_scheduling(self):
        if not self.animation_running:
            return
        
        if self.animation_paused:
            self.root.after(100, self.animate_scheduling)
            return
        
        max_time = max([r[2] for r in self.results]) if self.results else 0
        
        if self.current_time > max_time:
            self.animation_running = False
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.display_results()
            messagebox.showinfo("Complete", "Animation completed!")
            return
        
        self.draw_animated_gantt()
        self.update_process_status()
        
        self.current_time += 1
        self.time_label.config(text=f"Current Time: {self.current_time}")
        
        self.root.after(self.animation_speed, self.animate_scheduling)
    
    def draw_animated_gantt(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(set([r[0].pid for r in self.results]))))
        color_map = {pid: colors[i] for i, pid in enumerate(set([r[0].pid for r in self.results]))}
        
        # Draw completed portions
        for process, start, end in self.results:
            if start < self.current_time:
                actual_end = min(end, self.current_time)
                width = actual_end - start
                
                bar = ax.barh(0, width, left=start, height=0.5, 
                           color=color_map[process.pid], edgecolor='black', linewidth=2)
                
                # Add process label
                ax.text((start + actual_end) / 2, 0, process.pid, 
                       ha='center', va='center', fontweight='bold', fontsize=10)
                
                # Highlight currently running process
                if start <= self.current_time < end:
                    ax.barh(0, width, left=start, height=0.5, 
                           color=color_map[process.pid], edgecolor='red', 
                           linewidth=3, alpha=0.8)
        
        # Draw current time marker
        ax.axvline(x=self.current_time, color='red', linestyle='--', linewidth=2, label='Current Time')
        
        max_time = max([r[2] for r in self.results]) if self.results else 10
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlim(0, max_time + 1)
        ax.set_xlabel('Time', fontweight='bold', fontsize=11)
        ax.set_yticks([])
        ax.set_title(f'{self.algorithm_var.get()} Scheduling - Animation', 
                    fontweight='bold', fontsize=13)
        ax.grid(axis='x', alpha=0.3)
        ax.legend(loc='upper right')
        
        self.canvas.draw()
    
    def update_process_status(self):
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"⏰ TIME: {self.current_time}\n")
        self.status_text.insert(tk.END, "=" * 70 + "\n")
        
        # Find currently running process
        running_process = None
        for process, start, end in self.results:
            if start <= self.current_time < end:
                running_process = process
                self.status_text.insert(tk.END, f"🔄 RUNNING: {process.pid} ")
                self.status_text.insert(tk.END, f"[{start} → {end}] ")
                self.status_text.insert(tk.END, f"(Progress: {self.current_time - start}/{end - start})\n")
                break
        
        if not running_process:
            self.status_text.insert(tk.END, "💤 CPU IDLE\n")
        
        self.status_text.insert(tk.END, "-" * 70 + "\n")
        
        # Show waiting processes
        waiting = []
        completed = []
        
        for process, start, end in self.results:
            if start > self.current_time:
                if process.pid not in [p.pid for p in waiting]:
                    waiting.append(process)
            elif end <= self.current_time:
                if process.pid not in [p.pid for p in completed]:
                    completed.append(process)
        
        if waiting:
            self.status_text.insert(tk.END, "⏳ WAITING: ")
            self.status_text.insert(tk.END, ", ".join([p.pid for p in waiting]) + "\n")
        
        if completed:
            self.status_text.insert(tk.END, "✅ COMPLETED: ")
            self.status_text.insert(tk.END, ", ".join([p.pid for p in completed]) + "\n")
    
    def execute_scheduling(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process!")
            return
        
        algorithm = self.algorithm_var.get()
        
        if algorithm == "FCFS":
            self.fcfs_scheduling()
        elif algorithm == "SJF":
            self.sjf_scheduling()
        elif algorithm == "Priority":
            self.priority_scheduling()
        elif algorithm == "RR":
            try:
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    raise ValueError
                self.round_robin_scheduling(quantum)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid time quantum!")
                return
        
        self.display_results()
    
    def fcfs_scheduling(self):
        # Sort by arrival time
        sorted_processes = sorted(self.processes, key=lambda x: x.arrival_time)
        self.results = []
        current_time = 0
        
        for process in sorted_processes:
            p = Process(process.pid, process.arrival_time, process.burst_time, process.priority)
            
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            
            p.response_time = current_time - p.arrival_time
            start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            
            self.results.append((p, start_time, current_time))
    
    def sjf_scheduling(self):
        sorted_processes = sorted(self.processes, key=lambda x: x.arrival_time)
        self.results = []
        current_time = 0
        completed = []
        remaining = sorted_processes.copy()
        
        while remaining:
            # Get available processes
            available = [p for p in remaining if p.arrival_time <= current_time]
            
            if not available:
                current_time = remaining[0].arrival_time
                continue
            
            # Select shortest job
            shortest = min(available, key=lambda x: x.burst_time)
            remaining.remove(shortest)
            
            p = Process(shortest.pid, shortest.arrival_time, shortest.burst_time, shortest.priority)
            p.response_time = current_time - p.arrival_time
            start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            
            self.results.append((p, start_time, current_time))
    
    def priority_scheduling(self):
        sorted_processes = sorted(self.processes, key=lambda x: x.arrival_time)
        self.results = []
        current_time = 0
        remaining = sorted_processes.copy()
        
        while remaining:
            # Get available processes
            available = [p for p in remaining if p.arrival_time <= current_time]
            
            if not available:
                current_time = remaining[0].arrival_time
                continue
            
            # Select highest priority (lowest number)
            highest_priority = min(available, key=lambda x: x.priority)
            remaining.remove(highest_priority)
            
            p = Process(highest_priority.pid, highest_priority.arrival_time, 
                       highest_priority.burst_time, highest_priority.priority)
            p.response_time = current_time - p.arrival_time
            start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            
            self.results.append((p, start_time, current_time))
    
    def round_robin_scheduling(self, quantum):
        from collections import deque
        
        sorted_processes = sorted(self.processes, key=lambda x: x.arrival_time)
        self.results = []
        current_time = 0
        ready_queue = deque()
        remaining = sorted_processes.copy()
        process_dict = {}
        
        # Initialize process copies
        for p in sorted_processes:
            process_dict[p.pid] = Process(p.pid, p.arrival_time, p.burst_time, p.priority)
        
        # Add first process
        if remaining:
            ready_queue.append(remaining.pop(0))
        
        while ready_queue or remaining:
            if not ready_queue:
                current_time = remaining[0].arrival_time
                ready_queue.append(remaining.pop(0))
            
            current_process = ready_queue.popleft()
            p = process_dict[current_process.pid]
            
            if p.response_time == -1:
                p.response_time = current_time - p.arrival_time
            
            start_time = current_time
            execution_time = min(quantum, p.remaining_time)
            p.remaining_time -= execution_time
            current_time += execution_time
            
            self.results.append((p, start_time, current_time))
            
            # Add newly arrived processes
            while remaining and remaining[0].arrival_time <= current_time:
                ready_queue.append(remaining.pop(0))
            
            # Re-add current process if not finished
            if p.remaining_time > 0:
                ready_queue.append(current_process)
            else:
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
    
    def display_results(self):
        # Clear previous results
        self.figure.clear()
        self.stats_text.delete(1.0, tk.END)
        
        # Draw Gantt Chart
        ax = self.figure.add_subplot(111)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(set([r[0].pid for r in self.results]))))
        color_map = {pid: colors[i] for i, pid in enumerate(set([r[0].pid for r in self.results]))}
        
        for process, start, end in self.results:
            ax.barh(0, end - start, left=start, height=0.5, 
                   color=color_map[process.pid], edgecolor='black', linewidth=1.5)
            ax.text((start + end) / 2, 0, process.pid, 
                   ha='center', va='center', fontweight='bold', fontsize=9)
        
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlim(0, max([r[2] for r in self.results]) + 1)
        ax.set_xlabel('Time', fontweight='bold', fontsize=10)
        ax.set_yticks([])
        ax.set_title(f'{self.algorithm_var.get()} Scheduling - Gantt Chart', 
                    fontweight='bold', fontsize=12)
        ax.grid(axis='x', alpha=0.3)
        
        self.canvas.draw()
        
        # Display Statistics
        self.stats_text.insert(tk.END, "=" * 85 + "\n")
        self.stats_text.insert(tk.END, f"Algorithm: {self.algorithm_var.get()}\n")
        self.stats_text.insert(tk.END, "=" * 85 + "\n\n")
        
        self.stats_text.insert(tk.END, f"{'PID':<8} {'AT':<6} {'BT':<6} {'CT':<6} {'TAT':<6} {'WT':<6} {'RT':<6}\n")
        self.stats_text.insert(tk.END, "-" * 85 + "\n")
        
        # Collect unique processes
        unique_processes = {}
        for process, _, _ in self.results:
            if process.pid not in unique_processes or process.completion_time > 0:
                unique_processes[process.pid] = process
        
        total_tat = 0
        total_wt = 0
        total_rt = 0
        count = len(unique_processes)
        
        for pid, process in unique_processes.items():
            self.stats_text.insert(tk.END, 
                f"{process.pid:<8} {process.arrival_time:<6} {process.burst_time:<6} "
                f"{process.completion_time:<6} {process.turnaround_time:<6} "
                f"{process.waiting_time:<6} {process.response_time:<6}\n")
            
            total_tat += process.turnaround_time
            total_wt += process.waiting_time
            total_rt += process.response_time
        
        self.stats_text.insert(tk.END, "\n" + "=" * 85 + "\n")
        self.stats_text.insert(tk.END, f"Average Turnaround Time: {total_tat/count:.2f}\n")
        self.stats_text.insert(tk.END, f"Average Waiting Time:    {total_wt/count:.2f}\n")
        self.stats_text.insert(tk.END, f"Average Response Time:   {total_rt/count:.2f}\n")
        self.stats_text.insert(tk.END, "=" * 85 + "\n")
        
        # Add algorithm description
        descriptions = {
            "FCFS": "\n✓ First Come First Served\n✓ Simple & Fair\n✗ Convoy Effect (long process blocks short ones)",
            "SJF": "\n✓ Shortest Job First\n✓ Minimizes average waiting time\n✗ Starvation possible\n✗ Requires burst time estimation",
            "Priority": "\n✓ Higher priority processes execute first\n✗ Starvation (can be solved with aging)",
            "RR": "\n✓ Round Robin - Fair time sharing\n✓ Good for time-sharing systems\n✗ Context switching overhead if quantum too small"
        }
        
        self.stats_text.insert(tk.END, f"\n{descriptions[self.algorithm_var.get()]}\n")

def main():
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
