from datetime import datetime

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
    time_aggregation()


if __name__ == "__main__":
    main()
