import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

file_path = "original_script/performance_cores_original.csv"
df = pd.read_csv(file_path)

# Setting the style for the plots
sns.set_style("whitegrid")

# Plotting Time per Frame Over Time
plt.figure(figsize=(12, 6))
sns.lineplot(x=df['Frame'], y=df['time_in_us'])
plt.title('Inference Time per Frame Over Time')
plt.xlabel('Frame')
plt.ylabel('Inference Time (microseconds)')
plt.savefig("original_script/performance_cores_original.png")

"""
# Plotting Time per Frame Depending on Number of Cars
plt.figure(figsize=(12, 6))
sns.scatterplot(x=df['num_cars'], y=df['time_in_us'])
plt.title('Inference Time per Frame Depending on Number of Cars')
plt.xlabel('Number of Cars')
plt.ylabel('Inference Time (microseconds)')
plt.show()
"""