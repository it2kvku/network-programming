import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from enum import Enum

class PhilosopherState(Enum):
    THINKING = "Thinking"
    HUNGRY = "Hungry"
    EATING = "Eating"
    WAITING = "Waiting"
    DEADLOCKED = "Deadlocked"

class Fork:
    def __init__(self, fork_id):
        self.fork_id = fork_id
        self.lock = threading.Lock()
        self.owner = None
        self.available = True

class Philosopher(threading.Thread):
    def __init__(self, philosopher_id, left_fork, right_fork, callback, solution_type):
        super().__init__(daemon=True)
        self.philosopher_id = philosopher_id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.state = PhilosopherState.THINKING
        self.callback = callback
        self.solution_type = solution_type
        self.running = True
        self.eat_count = 0
        self.think_count = 0
        self.wait_count = 0
        self.max_wait_time = 0
        self.last_action_time = time.time()
        
    def run(self):
        while self.running:
            self.think()
            if not self.running:
                break
                
            if self.solution_type == "naive":
                self.eat_naive()
            elif self.solution_type == "ordering":
                self.eat_ordering()
            elif self.solution_type == "limit":
                self.eat_limit()
            elif self.solution_type == "asymmetric":
                self.eat_asymmetric()
    
    def think(self):
        self.state = PhilosopherState.THINKING
        self.think_count += 1
        self.callback(self)
        time.sleep(0.5 + (self.philosopher_id * 0.1))
    
    def eat_naive(self):
        """Naive solution - Prone to deadlock"""
        self.state = PhilosopherState.HUNGRY
        self.callback(self)
        
        wait_start = time.time()
        # Pick left fork first
        self.left_fork.lock.acquire()
        self.left_fork.owner = self.philosopher_id
        self.left_fork.available = False
        self.callback(self)
        time.sleep(0.3)  # Simulate delay
        
        # Try to pick right fork
        acquired = self.right_fork.lock.acquire(timeout=2)
        if acquired:
            self.right_fork.owner = self.philosopher_id
            self.right_fork.available = False
            wait_time = time.time() - wait_start
            self.max_wait_time = max(self.max_wait_time, wait_time)
            
            # Eating
            self.state = PhilosopherState.EATING
            self.eat_count += 1
            self.callback(self)
            time.sleep(1.0)
            
            # Release forks
            self.right_fork.lock.release()
            self.right_fork.owner = None
            self.right_fork.available = True
            self.left_fork.lock.release()
            self.left_fork.owner = None
            self.left_fork.available = True
        else:
            # Deadlock detected
            self.state = PhilosopherState.DEADLOCKED
            self.wait_count += 1
            self.callback(self)
            self.left_fork.lock.release()
            self.left_fork.owner = None
            self.left_fork.available = True
            time.sleep(0.5)
    
    def eat_ordering(self):
        """Resource ordering - Order forks by ID"""
        self.state = PhilosopherState.HUNGRY
        self.callback(self)
        
        wait_start = time.time()
        # Always pick lower numbered fork first
        first_fork = self.left_fork if self.left_fork.fork_id < self.right_fork.fork_id else self.right_fork
        second_fork = self.right_fork if self.left_fork.fork_id < self.right_fork.fork_id else self.left_fork
        
        first_fork.lock.acquire()
        first_fork.owner = self.philosopher_id
        first_fork.available = False
        self.callback(self)
        
        second_fork.lock.acquire()
        second_fork.owner = self.philosopher_id
        second_fork.available = False
        wait_time = time.time() - wait_start
        self.max_wait_time = max(self.max_wait_time, wait_time)
        
        # Eating
        self.state = PhilosopherState.EATING
        self.eat_count += 1
        self.callback(self)
        time.sleep(1.0)
        
        # Release forks
        second_fork.lock.release()
        second_fork.owner = None
        second_fork.available = True
        first_fork.lock.release()
        first_fork.owner = None
        first_fork.available = True
    
    def eat_limit(self):
        """Limit N-1 philosophers - Not implemented in thread, handled by semaphore in GUI"""
        self.eat_ordering()  # Use ordering logic
    
    def eat_asymmetric(self):
        """Asymmetric solution - Even pick left first, odd pick right first"""
        self.state = PhilosopherState.HUNGRY
        self.callback(self)
        
        wait_start = time.time()
        if self.philosopher_id % 2 == 0:
            # Even: left first
            first_fork = self.left_fork
            second_fork = self.right_fork
        else:
            # Odd: right first
            first_fork = self.right_fork
            second_fork = self.left_fork
        
        first_fork.lock.acquire()
        first_fork.owner = self.philosopher_id
        first_fork.available = False
        self.callback(self)
        
        second_fork.lock.acquire()
        second_fork.owner = self.philosopher_id
        second_fork.available = False
        wait_time = time.time() - wait_start
        self.max_wait_time = max(self.max_wait_time, wait_time)
        
        # Eating
        self.state = PhilosopherState.EATING
        self.eat_count += 1
        self.callback(self)
        time.sleep(1.0)
        
        # Release forks
        second_fork.lock.release()
        second_fork.owner = None
        second_fork.available = True
        first_fork.lock.release()
        first_fork.owner = None
        first_fork.available = True
    
    def stop(self):
        self.running = False

class DiningPhilosophersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dining Philosophers Problem Simulator")
        self.root.geometry("1600x900")
        self.root.configure(bg='#2c3e50')
        
        self.num_philosophers = 5
        self.philosophers = []
        self.forks = []
        self.running = False
        self.deadlock_detected = False
        self.semaphore = None
        
        # Colors for states
        self.state_colors = {
            PhilosopherState.THINKING: "#3498db",  # Blue
            PhilosopherState.HUNGRY: "#f39c12",    # Orange
            PhilosopherState.EATING: "#27ae60",    # Green
            PhilosopherState.WAITING: "#e67e22",   # Dark Orange
            PhilosopherState.DEADLOCKED: "#e74c3c" # Red
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="🍝 DINING PHILOSOPHERS PROBLEM 🥢", 
                font=('Arial', 20, 'bold'), bg='#34495e', fg='white').pack()
        tk.Label(title_frame, text="Classical Synchronization Problem Visualization", 
                font=('Arial', 11, 'italic'), bg='#34495e', fg='#bdc3c7').pack()
        
        # Create main container with scrollbar
        container = tk.Frame(self.root, bg='#2c3e50')
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(container, bg='#2c3e50')
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c3e50')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main container
        main_frame = tk.Frame(scrollable_frame, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Control
        left_frame = tk.LabelFrame(main_frame, text="Control Panel", 
                                   font=('Arial', 13, 'bold'), bg='#ecf0f1', 
                                   fg='#2c3e50', padx=15, pady=15)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Number of Philosophers
        tk.Label(left_frame, text="Number of Philosophers:", 
                bg='#ecf0f1', font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=10)
        self.num_phil_var = tk.IntVar(value=5)
        num_spinner = tk.Spinbox(left_frame, from_=3, to=10, textvariable=self.num_phil_var,
                                 width=10, font=('Arial', 11))
        num_spinner.grid(row=0, column=1, pady=10)
        
        # Solution Selection
        solution_frame = tk.LabelFrame(left_frame, text="Select Solution", 
                                       font=('Arial', 12, 'bold'), bg='#ecf0f1', 
                                       fg='#2c3e50', padx=10, pady=10)
        solution_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=15)
        
        self.solution_var = tk.StringVar(value="naive")
        solutions = [
            ("1. Naive (Deadlock-prone)", "naive"),
            ("2. Resource Ordering", "ordering"),
            ("3. Limit N-1 Philosophers", "limit"),
            ("4. Asymmetric Pick", "asymmetric")
        ]
        
        for i, (text, value) in enumerate(solutions):
            tk.Radiobutton(solution_frame, text=text, variable=self.solution_var,
                          value=value, bg='#ecf0f1', font=('Arial', 10),
                          anchor='w').grid(row=i, column=0, sticky='w', pady=3)
        
        # Control Buttons
        button_frame = tk.Frame(left_frame, bg='#ecf0f1')
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.start_btn = tk.Button(button_frame, text="▶ START", command=self.start_simulation,
                                   bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                   width=12, height=2, cursor='hand2')
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ STOP", command=self.stop_simulation,
                                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                                  width=12, height=2, cursor='hand2', state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.reset_btn = tk.Button(button_frame, text="🔄 RESET", command=self.reset_simulation,
                                   bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                                   width=12, height=2, cursor='hand2')
        self.reset_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Legend
        legend_frame = tk.LabelFrame(left_frame, text="State Legend", 
                                     font=('Arial', 11, 'bold'), bg='#ecf0f1',
                                     fg='#2c3e50', padx=10, pady=10)
        legend_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        states = [
            ("🧠 Thinking", PhilosopherState.THINKING),
            ("😋 Hungry", PhilosopherState.HUNGRY),
            ("🍝 Eating", PhilosopherState.EATING),
            ("⏳ Waiting", PhilosopherState.WAITING),
            ("🔴 Deadlocked", PhilosopherState.DEADLOCKED)
        ]
        
        for i, (text, state) in enumerate(states):
            color_box = tk.Label(legend_frame, text="  ", bg=self.state_colors[state],
                               relief=tk.RAISED, borderwidth=2)
            color_box.grid(row=i, column=0, padx=5, pady=2)
            tk.Label(legend_frame, text=text, bg='#ecf0f1', 
                    font=('Arial', 10), anchor='w').grid(row=i, column=1, sticky='w', pady=2)
        
        # Solution Description
        desc_frame = tk.LabelFrame(left_frame, text="Solution Description", 
                                   font=('Arial', 11, 'bold'), bg='#ecf0f1',
                                   fg='#2c3e50', padx=10, pady=10)
        desc_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.desc_text = tk.Text(desc_frame, height=12, width=40, wrap=tk.WORD,
                                font=('Arial', 9), bg='#fffacd', relief=tk.SUNKEN)
        self.desc_text.pack(fill=tk.BOTH, expand=True)
        self.update_description()
        
        # Middle panel - Visualization
        middle_frame = tk.Frame(main_frame, bg='#2c3e50')
        middle_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Canvas for visualization
        canvas_frame = tk.LabelFrame(middle_frame, text="Dining Table Visualization", 
                                     font=('Arial', 13, 'bold'), bg='#ecf0f1',
                                     fg='#2c3e50', padx=10, pady=10)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=600, height=600, 
                               bg='#34495e', highlightthickness=0)
        self.canvas.pack()
        
        # Right panel - Statistics
        right_frame = tk.Frame(main_frame, bg='#2c3e50')
        right_frame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)
        
        # Statistics Panel
        stats_frame = tk.LabelFrame(right_frame, text="📊 Real-time Statistics", 
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1',
                                    fg='#2c3e50', padx=10, pady=10)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar for statistics
        stats_scroll_frame = tk.Frame(stats_frame, bg='white')
        stats_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        stats_scrollbar = tk.Scrollbar(stats_scroll_frame)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(stats_scroll_frame, width=50, 
                                 font=('Courier', 9), bg='white', relief=tk.SUNKEN,
                                 yscrollcommand=stats_scrollbar.set, wrap=tk.WORD)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.config(command=self.stats_text.yview)
        
        # Performance Summary
        summary_frame = tk.LabelFrame(right_frame, text="⚡ Performance Summary", 
                                      font=('Arial', 11, 'bold'), bg='#ecf0f1',
                                      fg='#2c3e50', padx=10, pady=10)
        summary_frame.pack(fill=tk.BOTH, pady=5)
        
        self.summary_label = tk.Label(summary_frame, text="Press START to begin simulation", 
                                      font=('Arial', 10), bg='#fffacd', 
                                      justify=tk.LEFT, anchor='w', padx=10, pady=10)
        self.summary_label.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=2)  # Visualization gets more space
        main_frame.columnconfigure(2, weight=1)  # Statistics column
        main_frame.rowconfigure(0, weight=1)
        
        # Bind solution change
        self.solution_var.trace('w', lambda *args: self.update_description())
        
        # Initial draw
        self.draw_table()
    
    def update_description(self):
        descriptions = {
            "naive": """
🔴 NAIVE SOLUTION (Deadlock-prone)

📝 Algorithm:
• Each philosopher picks LEFT fork first
• Then picks RIGHT fork
• Eats, then releases both forks

⚠️ Problem:
• If ALL philosophers pick left fork simultaneously
• → Nobody can get right fork
• → DEADLOCK!

💡 Purpose:
Demonstrates WHY synchronization is needed.

❌ Not recommended for production!
            """,
            "ordering": """
🟢 RESOURCE ORDERING

📝 Algorithm:
• Assign numbers to forks (0, 1, 2, ...)
• Each philosopher ALWAYS picks lower-numbered fork first
• Then picks higher-numbered fork

✅ Advantages:
• Prevents circular wait
• NO DEADLOCK guaranteed

⚠️ Disadvantages:
• May cause STARVATION
• Some philosophers wait longer

🎯 Best for: Systems with static resources
            """,
            "limit": """
🟡 LIMIT N-1 PHILOSOPHERS

📝 Algorithm:
• Allow maximum N-1 philosophers to sit at table
• Use semaphore to limit concurrent access
• At least 1 seat always empty

✅ Advantages:
• Simple to implement
• NO DEADLOCK guaranteed
• At least one fork always available

⚠️ Disadvantages:
• Reduces parallelism
• One philosopher always waiting
• Lower throughput

🎯 Best for: Resource-constrained systems
            """,
            "asymmetric": """
🔵 ASYMMETRIC PICK

📝 Algorithm:
• EVEN philosophers: pick LEFT fork first
• ODD philosophers: pick RIGHT fork first
• This breaks symmetry!

✅ Advantages:
• Simple and elegant
• NO DEADLOCK
• Good parallelism
• Easy to implement

✅ No starvation issues
• Fair distribution

🎯 Best for: Real-world applications
⭐ RECOMMENDED SOLUTION!
            """
        }
        
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(tk.END, descriptions.get(self.solution_var.get(), ""))
    
    def start_simulation(self):
        if self.running:
            messagebox.showinfo("Info", "Simulation is already running!")
            return
        
        self.num_philosophers = self.num_phil_var.get()
        self.running = True
        self.deadlock_detected = False
        
        # Create forks
        self.forks = [Fork(i) for i in range(self.num_philosophers)]
        
        # Create semaphore for limit solution
        if self.solution_var.get() == "limit":
            self.semaphore = threading.Semaphore(self.num_philosophers - 1)
        
        # Create philosophers
        self.philosophers = []
        for i in range(self.num_philosophers):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % self.num_philosophers]
            
            philosopher = Philosopher(i, left_fork, right_fork, 
                                    self.update_philosopher_state,
                                    self.solution_var.get())
            self.philosophers.append(philosopher)
        
        # Start all philosophers
        for philosopher in self.philosophers:
            if self.solution_var.get() == "limit":
                # Wrap in semaphore control
                original_run = philosopher.run
                def limited_run(phil=philosopher):
                    while phil.running:
                        self.semaphore.acquire()
                        phil.think()
                        phil.eat_ordering()
                        self.semaphore.release()
                philosopher.run = limited_run
            
            philosopher.start()
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.num_phil_var.set(self.num_philosophers)  # Lock the value
        
        # Start monitoring
        self.monitor_deadlock()
        self.update_statistics()
    
    def stop_simulation(self):
        self.running = False
        for philosopher in self.philosophers:
            philosopher.stop()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def reset_simulation(self):
        self.stop_simulation()
        time.sleep(0.5)
        self.philosophers = []
        self.forks = []
        self.deadlock_detected = False
        self.stats_text.delete(1.0, tk.END)
        self.draw_table()
    
    def update_philosopher_state(self, philosopher):
        """Callback when philosopher state changes"""
        self.root.after(0, self.draw_table)
    
    def draw_table(self):
        self.canvas.delete("all")
        
        if not self.philosophers:
            # Draw empty table
            center_x, center_y = 300, 300
            self.canvas.create_oval(center_x - 100, center_y - 100,
                                   center_x + 100, center_y + 100,
                                   fill='#8b4513', outline='#654321', width=3)
            self.canvas.create_text(center_x, center_y, 
                                   text="🍽️\nDining Table\n\nPress START", 
                                   font=('Arial', 16, 'bold'), fill='white')
            return
        
        center_x, center_y = 300, 300
        radius = 200
        
        # Draw table
        self.canvas.create_oval(center_x - 100, center_y - 100,
                               center_x + 100, center_y + 100,
                               fill='#8b4513', outline='#654321', width=3)
        
        # Draw philosophers and forks
        num = len(self.philosophers)
        angle_step = 360 / num
        
        for i in range(num):
            angle = math.radians(i * angle_step - 90)
            
            # Philosopher position
            phil_x = center_x + radius * math.cos(angle)
            phil_y = center_y + radius * math.sin(angle)
            
            # Get philosopher state
            philosopher = self.philosophers[i]
            color = self.state_colors[philosopher.state]
            
            # Draw philosopher
            self.canvas.create_oval(phil_x - 30, phil_y - 30,
                                   phil_x + 30, phil_y + 30,
                                   fill=color, outline='black', width=3)
            self.canvas.create_text(phil_x, phil_y, 
                                   text=f"P{i}\n{philosopher.state.value}",
                                   font=('Arial', 9, 'bold'), fill='white')
            
            # Fork position (between philosophers)
            fork_angle = math.radians((i + 0.5) * angle_step - 90)
            fork_x = center_x + (radius - 50) * math.cos(fork_angle)
            fork_y = center_y + (radius - 50) * math.sin(fork_angle)
            
            # Get fork state
            fork = self.forks[i]
            fork_color = '#95a5a6' if fork.available else '#e74c3c'
            fork_text = f"F{i}\n" + ("Free" if fork.available else f"P{fork.owner}")
            
            # Draw fork
            self.canvas.create_rectangle(fork_x - 15, fork_y - 25,
                                         fork_x + 15, fork_y + 25,
                                         fill=fork_color, outline='black', width=2)
            self.canvas.create_text(fork_x, fork_y, text=fork_text,
                                   font=('Arial', 8, 'bold'), fill='white')
        
        # Draw status message
        if self.deadlock_detected:
            self.canvas.create_text(center_x, 50, 
                                   text="🔴 DEADLOCK DETECTED! 🔴",
                                   font=('Arial', 16, 'bold'), fill='#e74c3c')
    
    def monitor_deadlock(self):
        """Monitor for potential deadlock in naive solution"""
        if not self.running:
            return
        
        if self.solution_var.get() == "naive" and self.philosophers:
            # Check if all philosophers are waiting with left fork
            all_deadlocked = all(
                phil.state == PhilosopherState.DEADLOCKED or
                (not phil.left_fork.available and phil.left_fork.owner == phil.philosopher_id and
                 not phil.right_fork.available and phil.right_fork.owner != phil.philosopher_id)
                for phil in self.philosophers
            )
            
            if all_deadlocked and not self.deadlock_detected:
                self.deadlock_detected = True
                self.canvas.create_text(300, 50, 
                                       text="🔴 DEADLOCK DETECTED! 🔴",
                                       font=('Arial', 16, 'bold'), fill='#e74c3c',
                                       tags="deadlock")
        
        self.root.after(500, self.monitor_deadlock)
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.running:
            return
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "=" * 60 + "\n")
        self.stats_text.insert(tk.END, f"  SOLUTION: {self.solution_var.get().upper()}\n")
        self.stats_text.insert(tk.END, f"  PHILOSOPHERS: {len(self.philosophers)}\n")
        self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.stats_text.insert(tk.END, f"{'Phil':<5} {'State':<13} {'Ate':<5} {'Think':<6} {'Wait':<5} {'MaxWait':<8}\n")
        self.stats_text.insert(tk.END, "-" * 60 + "\n")
        
        total_eat = 0
        total_wait = 0
        max_wait_overall = 0
        
        for phil in self.philosophers:
            state_icon = {
                PhilosopherState.THINKING: "🧠",
                PhilosopherState.HUNGRY: "😋",
                PhilosopherState.EATING: "🍝",
                PhilosopherState.WAITING: "⏳",
                PhilosopherState.DEADLOCKED: "🔴"
            }
            
            self.stats_text.insert(tk.END, 
                f"P{phil.philosopher_id:<4} {state_icon[phil.state]} {phil.state.value:<10} "
                f"{phil.eat_count:<5} {phil.think_count:<6} {phil.wait_count:<5} "
                f"{phil.max_wait_time:.2f}s\n")
            
            total_eat += phil.eat_count
            total_wait += phil.wait_count
            max_wait_overall = max(max_wait_overall, phil.max_wait_time)
        
        self.stats_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.stats_text.insert(tk.END, f"💚 Total Meals Served: {total_eat}\n")
        self.stats_text.insert(tk.END, f"⏰ Total Wait Events: {total_wait}\n")
        self.stats_text.insert(tk.END, f"⏱️  Max Wait Time: {max_wait_overall:.2f}s\n")
        
        if self.deadlock_detected:
            self.stats_text.insert(tk.END, "\n" + "🔴" * 20 + "\n")
            self.stats_text.insert(tk.END, "⚠️  DEADLOCK DETECTED!\n")
            self.stats_text.insert(tk.END, "   System is stuck.\n")
            self.stats_text.insert(tk.END, "🔴" * 20 + "\n")
        
        self.stats_text.insert(tk.END, "=" * 60 + "\n")
        
        # Update performance summary
        avg_eat = total_eat / len(self.philosophers) if self.philosophers else 0
        efficiency = "🟢 EXCELLENT" if avg_eat > 10 else "🟡 GOOD" if avg_eat > 5 else "🟠 FAIR" if avg_eat > 2 else "🔴 POOR"
        
        deadlock_status = "🔴 YES - SYSTEM STUCK!" if self.deadlock_detected else "🟢 NO - RUNNING SMOOTHLY"
        
        summary_text = f"""
╔══════════════════════════════════════╗
║     PERFORMANCE METRICS              ║
╠══════════════════════════════════════╣
║ Avg Meals/Phil:  {avg_eat:.2f}           
║ Efficiency:      {efficiency}
║ Deadlock:        {deadlock_status}
║ Max Wait:        {max_wait_overall:.2f}s
╚══════════════════════════════════════╝
"""
        self.summary_label.config(text=summary_text, font=('Courier', 9, 'bold'))
        
        self.root.after(1000, self.update_statistics)

def main():
    root = tk.Tk()
    app = DiningPhilosophersGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
