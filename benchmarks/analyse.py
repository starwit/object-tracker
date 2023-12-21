import pandas as pd
import glob
import os

def scrape_and_analyze_csv_files(folder_path):

    #results = pd.DataFrame(columns=['Name of File', 'Mean Time', 'Standard Deviation', 'Min Time', 'Max Time'])
    results = pd.DataFrame()


    for file in glob.glob(os.path.join(folder_path, '*.csv')):

        # Read the CSV file

        data = pd.read_csv(file)
        print(data['time_in_us'].astype("int").mean())



        # Calculate the required statistics

        mean_time = data['time_in_us'].astype('int').mean()

        std_dev = data['time_in_us'].astype('int').std()

        min_time = data['time_in_us'].astype('int').min()

        max_time = data['time_in_us'].astype('int').max()



        # Extract the name of the file

        file_name = os.path.basename(file)


        results = pd.concat([results, pd.DataFrame([[file_name, mean_time, std_dev, min_time, max_time]])], ignore_index=True)


    return results

def analyse_csv(sw_version, file_name):
    data = pd.read_csv(f"benchmarks/{sw_version}/{file_name}.csv")

    # Calculate the required statistics

    mean_time = data['time_in_us'].astype('int').mean()

    std_dev = data['time_in_us'].astype('int').std()

    min_time = data['time_in_us'].astype('int').min()

    max_time = data['time_in_us'].astype('int').max()


    print(f"\nmean:{mean_time}, standard_dev: {std_dev}, min: {min_time}, max: {max_time}")


#if __name__ == '__main__':
    #print(scrape_and_analyze_csv_files("original_script"))