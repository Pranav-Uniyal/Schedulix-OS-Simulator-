# 🧠 Schedulix - Ultimate OS Scheduling Simulator

Schedulix is a visually rich, interactive simulator for understanding and analyzing CPU scheduling algorithms. Built with Python and Tkinter, this simulator supports **FCFS**, **SJF (Preemptive & Non-preemptive)**, **Priority**, and **Round Robin** scheduling. It includes **real-time Gantt chart animations**, **detailed performance metrics**, and **visual comparisons** of all algorithms.





---

## 🚀 Features

- 🔁 **Supports 5 major algorithms:**
  - FCFS (First Come First Serve)
  - SJF (Preemptive & Non-preemptive)
  - Priority Scheduling
  - Round Robin (with configurable quantum)

- 📊 **Metrics Tracked:**
  - Completion Time (CT)
  - Turnaround Time (TAT)
  - Waiting Time (WT)
  - Response Time (RT)
  - Throughput

- 🎥 **Live Animation:**
  - Real-time Gantt Chart simulation with timeline progress and CPU idle time representation.

- 📈 **Graphical Summary:**
  - Individual bar chart for selected algorithm.
  - Comparative bar chart to visualize metrics across multiple algorithms.

- 🖥️ **Beautiful UI:**
  - Futuristic dark theme
  - Scrollable logs
  - Instant error validation and success logs

---

## 📦 Requirements

Make sure you have Python 3.x and the following libraries installed:

```bash
pip install matplotlib numpy
```

---

## 🛠️ How to Run

1. Clone this repository or download the script:
   ```bash
   git clone https://github.com/Pranav-Uniyal/Schedulix-OS-Simulator-.git
   cd Schedulix-OS-Simulator-
   ```

2. Run the simulator:
   ```bash
   python main.py
   ```
---

## 📸 Screenshots

![image](https://github.com/user-attachments/assets/f24442e6-838d-496b-b9d2-7fc892d7516f)
![image](https://github.com/user-attachments/assets/9616fe98-b5dc-4ba5-8f92-2ca09a62e85b)

---

## 🧩 Project Structure

- `SchedulixSimulator` class: Core logic and GUI management.
- `run_algorithm` dispatcher: Dynamically selects the chosen scheduling algorithm.
- `draw_bar`, `draw_time_markers`: Handles animated Gantt chart.
- `show_metrics`, `draw_algorithm_graph`: Performance visualization and summary.
- `compare_all_algorithms`: Visual comparison of all metrics across multiple algorithms.

---

## 📚 Educational Value

Schedulix is ideal for:

- OS Course Assignments & Labs
- Teaching tool in classrooms
- Students learning CPU scheduling practically

---

## 🌐 Web Version (In Development)

We're currently working on **Schedulix Web 3D** — a next-generation, browser-based version of the simulator that brings **CPU scheduling to life in 3D**.

### 🔮 What to Expect

- 🧊 **3D Visualization** of process scheduling using **Three.js** and **React Three Fiber**
- 🌀 **Realistic physics simulation** powered by **Rapier Physics Engine**
- 🌍 **Cross-platform accessibility** — run entirely in the browser
- ⚙️ Built with **React**, **Three.js**, **Zustand**, **GSAP**, and other modern frontend tools
- 🎓 Designed for an engaging, interactive learning experience for OS concepts

> 🚧 *Currently under development — this web version will elevate traditional CPU scheduling simulators into a dynamic, gamified learning platform.*

📌 **Live Demo & Repository Coming Soon!**

## 👨‍💻 Author

Developed by **Pranav Uniyal**, **Srijan Petwal**, **Parthvi Sah**, **Soni Pathak**  
Feel free to connect on [GitHub](https://github.com/Pranav-Uniyal) or [LinkedIn](https://www.linkedin.com/in/pranav-uniyal-894801251/).

---

