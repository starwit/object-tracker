import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot(sw_version, file_name):
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
    plt.savefig(f"benchmarks/{sw_version}/{file_name}.png")

