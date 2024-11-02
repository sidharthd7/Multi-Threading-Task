import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool, cpu_count
import psutil
import threading

def multiply_matrices(constant_matrix, matrix):
    return np.dot(constant_matrix, matrix)

# execution time with different thread counts
def measure_execution_time(num_threads, matrices, constant_matrix, cpu_usage_log):
    stop_monitoring = threading.Event()
    monitor_thread = threading.Thread(target=monitor_cpu_usage, args=(cpu_usage_log, stop_monitoring))
    monitor_thread.start()
    
    with Pool(processes=num_threads) as pool:
        start_time = time.time()
        pool.starmap(multiply_matrices, [(constant_matrix, m) for m in matrices])
        end_time = time.time()
    
    # Stop CPU monitoring
    stop_monitoring.set()
    monitor_thread.join()
    return end_time - start_time

# for CPU usage logging
def monitor_cpu_usage(cpu_usage_log, stop_event):
    while not stop_event.is_set():
        usage = psutil.cpu_percent(interval=0.5, percpu=True)
        cpu_usage_log.append(usage)
        
def main():
    matrix_size = 500
    num_matrices = 500
    constant_matrix = np.random.rand(matrix_size, matrix_size)
    matrices = [np.random.rand(matrix_size, matrix_size) for _ in range(num_matrices)]

    # no. of threads 
    num_threads_list = list(range(1, 9))  

    times_taken = []
    cpu_usage_records = []

    # matrix multiplication with different thread counts
    for num_threads in num_threads_list:
        print(f"\nTesting with {num_threads} threads...")
        # Store CPU usage for this run
        cpu_usage_log = []
        # Measure execution time
        time_taken = measure_execution_time(num_threads, matrices, constant_matrix, cpu_usage_log)
        times_taken.append(time_taken)
        cpu_usage_records.append(cpu_usage_log)
        print(f"Time taken with {num_threads} threads: {time_taken:.2f} seconds")

    # execution time graph
    plt.figure(figsize=(8, 6))
    plt.plot(num_threads_list, [t / 60 for t in times_taken], marker='o', color='b', label="Execution Time")
    plt.xlabel("Number of Threads")
    plt.ylabel("Time Taken (minutes)")
    plt.title("Execution Time vs. Number of Threads")
    plt.xticks(num_threads_list)
    plt.legend()
    plt.grid(True)
    plt.show()

    # displaying CPU usage
    plt.figure(figsize=(12, 8))
    for i, cpu_usage_log in enumerate(cpu_usage_records):
        avg_cpu_usage = [sum(core_usage) / len(core_usage) for core_usage in cpu_usage_log]
        plt.plot(avg_cpu_usage, label=f'{num_threads_list[i]} Threads')
    plt.xlabel("Time (0.5 sec intervals)")
    plt.ylabel("Average CPU Usage (%)")
    plt.title("CPU Usage Over Time for Different Thread Counts")
    plt.legend()
    plt.grid(True)
    plt.show()

    data = {
        "Threads": [f"T={t}" for t in num_threads_list],
        "Time Taken (min)": [t / 60 for t in times_taken]
    }
    df = pd.DataFrame(data)

    styled_table = df.style.set_caption("Execution Time for Different Thread Counts") \
                        .set_properties(**{'text-align': 'center'}) \
                        .set_table_styles([{
                            'selector': 'th',
                            'props': [('text-align', 'center')]
                        }])

    styled_table

    fig, ax = plt.subplots(figsize=(8, 2)) 
    ax.axis('tight')
    ax.axis('off')
    sns.heatmap(df.set_index("Threads"), annot=True, fmt=".2f", cmap="YlGnBu", cbar=False, linewidths=0.5, annot_kws={"size": 12}, ax=ax)
    plt.title("Execution Time for Different Thread Counts", loc="center", fontsize=14, fontweight='bold')
    plt.savefig("execution_time_table.png", bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
