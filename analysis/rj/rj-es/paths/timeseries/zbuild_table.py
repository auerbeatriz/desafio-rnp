import json
import os
import csv
from collections import defaultdict


def load_latency_data_from_txt(paths_dir):
    """
    Carrega dados de latência de arquivos TXT individuais por caminho.
    
    Args:
        paths_dir: Diretório contendo os arquivos *_timeseries.txt
    
    Returns:
        Dicionário {path_id: {timestamp: latency}}
    """
    latency_by_path = {}
    
    # Lista todos os arquivos _timeseries.txt
    for filename in sorted(os.listdir(paths_dir)):
        if not filename.endswith('_timeseries.txt'):
            continue
        
        # Extrai o path_id do nome do arquivo (ex: 0_timeseries.txt -> 0)
        path_id = int(filename.replace('_timeseries.txt', ''))
        
        filepath = os.path.join(paths_dir, filename)
        latency_by_path[path_id] = {}
        
        # Lê o arquivo
        with open(filepath, 'r') as f:
            next(f)  # Pula cabeçalho
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                timestamp, latency = line.split(',')
                latency_by_path[path_id][int(timestamp)] = float(latency)
    
    return latency_by_path


def load_latency_data_from_json(json_filepath):
    """
    Carrega dados de latência de um arquivo JSON consolidado.
    
    Args:
        json_filepath: Caminho para o arquivo latency.json
    
    Returns:
        Dicionário {path_id: {timestamp: latency}}
    """
    latency_by_path = defaultdict(dict)
    
    with open(json_filepath, 'r') as f:
        data = json.load(f)
    
    for entry in data:
        timestamp = entry['timestamp']
        for lat_info in entry['latency']:
            path_id = lat_info['path_id']
            rtt = lat_info['rtt']
            
            if rtt is not None:
                latency_by_path[path_id][timestamp] = rtt
    
    return dict(latency_by_path)


def build_latency_matrix(latency_by_path, output_filepath):
    """
    Constrói matriz de latência com timestamps nas linhas e paths nas colunas.
    
    Args:
        latency_by_path: Dicionário {path_id: {timestamp: latency}}
        output_filepath: Caminho do arquivo CSV de saída
    """
    # Coleta todos os timestamps únicos
    all_timestamps = set()
    for path_data in latency_by_path.values():
        all_timestamps.update(path_data.keys())
    
    # Ordena timestamps
    sorted_timestamps = sorted(all_timestamps)
    
    # Ordena path_ids
    sorted_path_ids = sorted(latency_by_path.keys())
    
    # Escreve CSV
    with open(output_filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Cabeçalho
        header = ['timestamp'] + [f'path_{pid}' for pid in sorted_path_ids]
        writer.writerow(header)
        
        # Dados
        for ts in sorted_timestamps:
            row = [ts]
            
            for path_id in sorted_path_ids:
                # Pega latência ou NaN se não existir
                latency = latency_by_path[path_id].get(ts, float('nan'))
                row.append(latency)
            
            writer.writerow(row)
    
    return len(sorted_timestamps), len(sorted_path_ids)


def print_summary(output_filepath, num_timestamps, num_paths):
    """
    Imprime resumo da matriz criada.
    """
    print(f"\n{'='*70}")
    print("✓ MATRIZ DE LATÊNCIA CRIADA COM SUCESSO")
    print(f"{'='*70}")
    print(f"Arquivo: {output_filepath}")
    print(f"Dimensões: {num_timestamps} timestamps × {num_paths} caminhos")
    print(f"{'='*70}\n")


def main():
    # Configurações
    origin = 'rj'
    destination = 'es'
    
    # Opção 1: Carregar de arquivos TXT individuais
    paths_dir = f'analysis/{origin}/{origin}-{destination}/paths/timeseries'
    
    # Opção 2: Carregar de JSON consolidado (comentar a linha acima e descomentar as linhas abaixo)
    # json_filepath = f'analysis/telemetry/{origin}/{origin}-{destination}/latency.json'
    # latency_by_path = load_latency_data_from_json(json_filepath)
    
    print(f"📂 Carregando dados de latência...")
    
    # Carrega dados (usando TXT por padrão)
    if os.path.exists(paths_dir):
        latency_by_path = load_latency_data_from_txt(paths_dir)
        print(f"✓ Dados carregados de arquivos TXT: {len(latency_by_path)} caminhos")
    else:
        print(f"❌ Diretório não encontrado: {paths_dir}")
        return
    
    # Verifica se há dados
    if not latency_by_path:
        print("❌ Nenhum dado de latência encontrado")
        return
    
    # Constrói matriz
    output_filepath = f'analysis/{origin}/{origin}-{destination}/latency_matrix.csv'
    
    print(f"\n📊 Construindo matriz de latência...")
    num_timestamps, num_paths = build_latency_matrix(latency_by_path, output_filepath)
    
    # Resumo
    print_summary(output_filepath, num_timestamps, num_paths)


if __name__ == "__main__":
    main()