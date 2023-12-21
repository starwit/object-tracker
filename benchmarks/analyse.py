import pandas as pd

def analyse_csv(sw_version, file_name):
    data = pd.read_csv(f"benchmarks/{sw_version}/{file_name}.csv")

    # Calculate the required statistics

    mean_time = data['time_in_us'].astype('int').mean()

    std_dev = data['time_in_us'].astype('int').std()

    min_time = data['time_in_us'].astype('int').min()

    max_time = data['time_in_us'].astype('int').max()


    print(f"\nmean:{mean_time}, standard_dev: {std_dev}, min: {min_time}, max: {max_time}")


