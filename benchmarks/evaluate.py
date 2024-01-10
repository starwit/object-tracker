import pandas as pd
import glob
import os

import matplotlib.pyplot as plt
import seaborn as sns



def scrape_and_analyze_csv_files(folder_path):

    #results = pd.DataFrame(columns=['Name of File', 'Mean Time', 'Standard Deviation', 'Min Time', 'Max Time'])
    results = pd.DataFrame()


    for file in glob.glob('./**/*.csv', recursive=True):

        # Read the CSV file
        data = pd.read_csv(file)
      
        # Calculate the required statistics

        mean_time = data['time_in_us'].astype('int').mean()

        std_dev = data['time_in_us'].astype('int').std()

        min_time = data['time_in_us'].astype('int').min()

        max_time = data['time_in_us'].astype('int').max()

        file_name = os.path.basename(file)[:-4]

        cut_string = lambda s: s.rpartition('_')[0]
        cores = cut_string(file_name)
        if cores == "performance":
            cores = "0-7"
        

        if "boxmot" in file:
            algorithm = os.path.normpath(file).split(os.sep)[1]
            
            results = pd.concat([results, pd.DataFrame([["boxmot", algorithm, cores, mean_time, std_dev, min_time, max_time]])], ignore_index=True)

        else:
            results = pd.concat([results, pd.DataFrame([["original_script", "deepocsort", cores, mean_time, std_dev, min_time, max_time]])], ignore_index=True)

    results.columns = ["Source", "Algorithm",'Cores', 'mean', 'std_dev', 'min_time', 'max_time']
    results = results.sort_values('mean')

    return results

def num_cars_performance(folder_path):
     for file in glob.glob(os.path.join(folder_path, '*.csv')):

        # Read the CSV file

        data = pd.read_csv(file)

        # Create a boxplot

        plt.figure(figsize=(10, 6))

        sns.boxplot(x='num_cars', y='time_in_us', data=data)

        plt.title('Number of Cars vs Time in Frame')

        plt.xlabel('Number of Cars')

        plt.ylabel('Time in Frame (us)')



        # Extract the name of the file without extension

        file_name = os.path.splitext(os.path.basename(file))[0]



        # Save the plot in the same folder with a modified file name

        plot_file_name = os.path.join(folder_path, f'{file_name}_boxplot.png')

        plt.savefig(plot_file_name)

        plt.close()

        


if __name__ == '__main__':
    print(scrape_and_analyze_csv_files(""))
    #num_cars_performance("original_script")