import glob
import os
import pandas as pd



def init_folders(dirs):
    # Check if the output directory exists
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Created output directory: {dir}")
    
def read_data(input_dir):
    input_files = glob.glob(os.path.join(input_dir, '*'))
    input_files.sort()
    return input_files

def get_dfs(questions_dir, static_filename="static_q_and_a.csv", audience_filename="q_and_a_audience.csv"):
    collected_csv_path = os.path.join(questions_dir, "q_and_a_audience.csv")
    static_csv_path = os.path.join(questions_dir, "static_q_and_a.csv")
    collected_df = translate_data(collected_csv_path)
    static_df = translate_data(static_csv_path)
    joined_df = pd.concat([collected_df, static_df])     
    return joined_df

def translate_data(csv_path, sep="|"):
    df = df = pd.read_csv(csv_path, sep=sep,)
    ratios = []
    for number in df["numbers"]:
        if '%' in number:
            value = number.replace("%", "")
            ratio = float(value)/100
        elif 'jours' in number:
            ratio = 1.0
        else:
            value = int(number)
            length = len(str(value))
            max_length = int('9' * length)
            ratio = value/max_length
        ratios.append(ratio)
    df["ratio"] = ratios
    return df
