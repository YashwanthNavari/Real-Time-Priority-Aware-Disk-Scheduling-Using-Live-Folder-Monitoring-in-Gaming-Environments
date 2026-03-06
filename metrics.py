import matplotlib.pyplot as plt

def plot_metrics(results):
    algorithms = [r["Algorithm"] for r in results]
    seek_times = [r["Total Seek Time"] for r in results]
    waiting_times = [r["Average Waiting Time"] for r in results]
    throughputs = [r["Throughput"] for r in results]

    # Plot Seek Time
    plt.figure(figsize=(10, 5))
    plt.bar(algorithms, seek_times, color='skyblue')
    plt.title('Total Seek Time vs Algorithm')
    plt.ylabel('Tracks')
    plt.savefig('seek_time_comparison.png')
    
    # Plot Average Waiting Time
    plt.figure(figsize=(10, 5))
    plt.bar(algorithms, waiting_times, color='lightgreen')
    plt.title('Average Waiting Time (s) vs Algorithm')
    plt.ylabel('Seconds')
    plt.savefig('waiting_time_comparison.png')
    
    # Plot Throughput
    plt.figure(figsize=(10, 5))
    plt.bar(algorithms, throughputs, color='salmon')
    plt.title('Throughput vs Algorithm')
    plt.ylabel('Requests / Second')
    plt.savefig('throughput_comparison.png')

    print("Graphs successfully generated: seek_time_comparison.png, waiting_time_comparison.png, throughput_comparison.png")
