import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_time(sw_version, file_name):
    file_path = f"benchmarks/{sw_version}/{file_name}.csv"
    df = pd.read_csv(file_path)

    # Setting the style for the plots
    sns.set_style("whitegrid")

    # Plotting Time per Frame Over Time
    plt.figure(figsize=(12, 6))

    sns.lineplot(x=df['Frame'], y=df['time_in_us'])

    plt.title(f'Inference Time per Frame ({file_name})')

    plt.xlabel('Frame')

    plt.ylabel('Inference Time (microseconds)')

    plt.savefig(f"benchmarks/{sw_version}/{file_name}_t_per_frame.png")
    
    plt.close()

def plot_time_num_cars(sw_version, file_name):

    file = f"benchmarks/{sw_version}/{file_name}.csv"

    data = pd.read_csv(file)

    # Create a boxplot

    plt.figure(figsize=(10, 6))

    sns.boxplot(x='num_cars', y='time_in_us', data=data)

    plt.title('Number of Cars vs Time in Frame')

    plt.xlabel('Number of Cars')

    plt.ylabel('Time in Frame (us)')

    # Save the plot in the same folder with a modified file name

    plt.savefig(f"benchmarks/{sw_version}/{file_name}_t_num_cars.png")

    plt.close()