from datetime import datetime
import numpy as np
import os
import pandas as pd

def generate_route_labels(filepath):
    df = pd.read_csv(filepath)
    rows = df.iloc[:, 1:].values

    min_path_ids = []
    for row_latencies in rows:
        # Encontra o índice do menor valor (tratando nan)
        # Converte para 1-based: path_1 = 1, path_2 = 2...
        min_idx = np.nanargmin(row_latencies)
        min_path_ids.append(int(min_idx + 1))

    print(min_path_ids[:20])
    
    output_filepath = filepath.replace('_latency.csv', '_labels.txt')

    with open(output_filepath, 'w') as f:
        for path_id in min_path_ids:
            f.write(f"{path_id}\n")

def interval_counter(root_dir):
    timeseries_dir = f'{root_dir}/paths/timeseries'
    out_dir = f'{root_dir}/paths/timeseries/intervals'

    files = [f for f in os.listdir(timeseries_dir) if os.path.isfile(os.path.join(timeseries_dir, f))]

    for f in files:
        filepath = os.path.join(timeseries_dir, f)
        out_filepath = os.path.join(out_dir, f)

        with open(out_filepath, 'w', encoding='utf-8') as fout:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    next_line = f.readline()

                    timestamp1 = line.split(',')[0]
                    timestamp2 = next_line.split(',')[0]

                    if(timestamp2 != ''):
                        dt_object1 = datetime.fromtimestamp(int(timestamp1))
                        dt_object2 = datetime.fromtimestamp(int(timestamp2))

                        time_difference = dt_object2 - dt_object1

                        fout.write(f'{time_difference}\n')

def time_aggregation():
    ids = [0, 1, 2]

    timestamps = []
    out_filepath = 'timestamps.txt'

    for pathid in ids:
        with open(out_filepath, 'w') as fout:
            filepath = f'{pathid}_timeseries.txt'

            with open(filepath, 'r') as f:
                for line in f:
                    if line == 'timestamp,latency_ms\n':
                        continue
                    
                    timestamp1 = line.split(',')[0]
                    timestamps.append(f'{timestamp1},{pathid}')
            
            timestamps.sort()
            tuple(timestamps)

            for t in timestamps:
                fout.write(f'{t}\n')

def main():
    # origin = 'rj'
    # destination = 'df'

    # root_dir = f'analysis/{origin}/{origin}-{destination}'

    # interval_counter(root_dir)
    # time_aggregation()

    filepath = 'analysis/rj/rj-es/ml/routes_latency.csv'
    generate_route_labels(filepath)


if __name__ == "__main__":
    main()
