import pandas as pd
import glob
import os

def scrape_and_analyze_csv_files(folder_path):

    #results = pd.DataFrame(columns=['Name of File', 'Mean Time', 'Standard Deviation', 'Min Time', 'Max Time'])
    results = pd.DataFrame()


    for file in glob.glob(os.path.join(folder_path, '*.csv')):

        # Read the CSV file

        data = pd.read_csv(file)

        # Calculate the required statistics

        mean_time = data['time_in_us'].astype('int').mean()

        std_dev = data['time_in_us'].astype('int').std()

        min_time = data['time_in_us'].astype('int').min()

        max_time = data['time_in_us'].astype('int').max()



        # Extract the name of the file

        file_name = os.path.basename(file)


        results = pd.concat([results, pd.DataFrame([[file_name, mean_time, std_dev, min_time, max_time]])], ignore_index=True)

    results.columns = ['File_name', 'mean', 'std_dev', 'min_time', 'max_time']
    results = results.sort_values('mean')

    return results

if __name__ == '__main__':
    print(scrape_and_analyze_csv_files("original_script"))