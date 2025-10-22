import pandas as pd
from io import StringIO
from os import listdir
from os.path import isfile, join


def save_interpolation(df_interpolated, out_dir):
    df_final = df_interpolated.reset_index(drop = True)

    filepath = join(out_dir, 'latency_matrix_interpolated.csv')
    df_final.to_csv(filepath, index=False)

    print(f"Sucesso! O arquivo '{filepath}' foi salvo.")

def load_interpolated_data(root_dir):
    files = [f for f in listdir(root_dir) if isfile(join(root_dir, f))]

    dfs = []
    
    for f in files:
        filepath = join(root_dir, f)

        df = pd.read_csv(filepath)

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.set_index('timestamp')

        df_minute = df.resample('10min').nearest()
        df_interpolated = df_minute.interpolate(method='linear', limit_direction='both')

        dfs.append(df_interpolated)
    
    return dfs

def rename_columns(dfs):
    renamed_dfs = []

    for i, df in enumerate(dfs):
        df = df.rename(columns={df.columns[0]: f"latency_{i+1}"})
        renamed_dfs.append(df)
    
    return renamed_dfs

def join_data(dfs):
    merged_df = dfs[0]

    for i in range(1, len(dfs)):
        merged_df = pd.merge_asof(merged_df, dfs[i], on='timestamp', direction='nearest')

    return merged_df

def main():
    origin = 'rj'
    destination = 'es'

    root_dir = f'analysis/{origin}/{origin}-{destination}/paths/timeseries'
    out_dir = f'analysis/{origin}/{origin}-{destination}'

    dfs = load_interpolated_data(root_dir)
    dfs = rename_columns(dfs)

    merged_df = join_data(dfs)

    save_interpolation(merged_df, out_dir)



if __name__ == "__main__":
    main()