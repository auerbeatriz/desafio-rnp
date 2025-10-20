from datetime import datetime
import numpy as np


def generate_route_labels(filepath):
    data = np.loadtxt(filepath)
    
    timestamps = data[:, 0]
    latencies = data[:, 1:] 
    
    min_path_ids = []
    for row_latencies in latencies:
        # Encontra índice do menor valor (0-based)
        # Converte para 1-based (path_1 = 1, path_2 = 2, etc)
        min_idx = np.nanargmin(row_latencies)
        min_path_ids.append(min_idx + 1)
    
    output_filepath = filepath.replace('routes_latency.txt', 'routes_label.txt')
    
    with open(output_filepath, 'w') as f:
        for path_id in min_path_ids:
            f.write(f"{path_id}\n")

def interval_counter():
    filepath = '2_timeseries.txt'
    out_filepath = '2_timeintervals.txt'

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
    #interval_counter()
    #time_aggregation()

    filepath = 'analysis/rj/rj-es/routes_latency.txt'
    generate_route_labels(filepath)
    print("--")


if __name__ == "__main__":
    main()
