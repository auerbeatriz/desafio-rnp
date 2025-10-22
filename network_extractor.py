import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict


def create_output_directories(origin, destination):
    """
    Cria a estrutura de diretórios para saída.
    
    Args:
        origin: Nome da origem
        destination: Nome do destino
    
    Returns:
        Tupla com (diretório base, diretório paths)
    """
    base_path = os.path.join('analysis', origin, f'{origin}-{destination}')
    paths_path = os.path.join(base_path, 'paths')
    os.makedirs(paths_path, exist_ok=True)
    return base_path, paths_path


def extract_path_from_hops(hops):
    """
    Extrai o caminho (sequência de IPs) de uma lista de hops.
    Descarta hops sem IP.
    
    Args:
        hops: Lista de hops do traceroute
    
    Returns:
        Lista com os IPs do caminho
    """
    path = []
    for hop in hops:
        if 'ip' in hop and hop['ip']:
            path.append(hop['ip'])
    return path


def extract_rtt_from_hops(hops):
    """
    Extrai o último RTT válido (latência ponta a ponta).
    
    Args:
        hops: Lista de hops do traceroute
    
    Returns:
        RTT do último hop ou None
    """
    for hop in reversed(hops):
        if 'ip' in hop and hop['ip'] and 'rtt' in hop and hop['rtt'] is not None:
            return hop['rtt']
    return None


def process_traceroute_data(traceroute_data, destination_ip):
    """
    Processa os dados do traceroute e agrupa medições por caminho.
    Considera a ORDEM dos IPs no caminho.
    FILTRA apenas medições que terminam no IP de destino especificado.
    
    Args:
        traceroute_data: Lista de medições de traceroute
        destination_ip: IP de destino esperado (último salto)
    
    Returns:
        Tupla com:
        - measurements_by_path: {path_id: [lista de medições completas]}
        - path_to_nodes: {path_id: [lista ordenada de IPs]}
        - G: Grafo NetworkX não direcionado
        - filtered_count: Número de medições filtradas
    """
    G = nx.Graph()
    path_to_id = {}
    path_to_nodes = {}
    path_counter = 0
    measurements_by_path = defaultdict(list)
    filtered_count = 0
    
    for entry in traceroute_data:
        hops = entry.get('val', [])
        
        # Extrai o caminho (sequência ordenada de IPs)
        path = extract_path_from_hops(hops)
        
        # Descarta medições sem caminho válido
        if not path:
            filtered_count += 1
            continue
        
        # FILTRO: Descarta medições que NÃO terminam no IP de destino
        if path[-1] != destination_ip:
            filtered_count += 1
            continue
        
        # Converte para tupla para usar como chave (mantém ordem)
        path_tuple = tuple(path)
        
        # Adiciona nós e arestas ao grafo
        previous_node = None
        for node in path:
            G.add_node(node)
            if previous_node is not None:
                G.add_edge(previous_node, node)
            previous_node = node
        
        # Identifica ou registra o caminho
        if path_tuple not in path_to_id:
            path_id = path_counter
            path_to_id[path_tuple] = path_id
            path_to_nodes[path_id] = list(path)
            path_counter += 1
        else:
            path_id = path_to_id[path_tuple]
        
        # Adiciona a medição completa ao caminho
        measurements_by_path[path_id].append(entry)
    
    return measurements_by_path, path_to_nodes, G, filtered_count


def export_path_measurements_json(paths_path, path_id, measurements):
    """
    Exporta as medições de um caminho para JSON.
    
    Args:
        paths_path: Diretório paths
        path_id: ID do caminho
        measurements: Lista de medições
    
    Returns:
        Caminho do arquivo criado
    """
    filepath = os.path.join(paths_path, f'{path_id}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(measurements, f, indent=4, ensure_ascii=False)
    return filepath


def export_path_timeseries(paths_path, path_id, measurements):
    """
    Exporta série temporal (timestamp, latência) para um caminho.
    
    Args:
        paths_path: Diretório paths
        path_id: ID do caminho
        measurements: Lista de medições
    
    Returns:
        Caminho do arquivo criado
    """
    filepath = os.path.join(paths_path, f'{path_id}_timeseries.txt')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("timestamp,latency_ms\n")
        
        for entry in measurements:
            timestamp = entry.get('ts')
            hops = entry.get('val', [])
            latency = extract_rtt_from_hops(hops)
            
            if timestamp is not None and latency is not None:
                f.write(f"{timestamp},{latency}\n")
    
    return filepath


def find_all_simple_paths(G, origin, destination):
    """
    Encontra todos os caminhos simples entre origem e destino.
    
    Args:
        G: Grafo NetworkX
        origin: Nó de origem
        destination: Nó de destino
    
    Returns:
        Lista de caminhos encontrados (ordenados por tamanho)
    """
    try:
        all_paths = list(nx.all_simple_paths(G, origin, destination))
        all_paths.sort(key=len)
        return all_paths
    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return []


def export_consolidated_report(base_path, measurements_by_path, path_to_nodes, G, 
                               origin_name, destination_name, origin_ip, destination_ip,
                               filtered_count, total_measurements):
    """
    Exporta relatório consolidado com todas as informações.
    
    Args:
        base_path: Diretório base de saída
        measurements_by_path: Medições agrupadas por caminho
        path_to_nodes: Mapeamento path_id -> lista de IPs
        G: Grafo NetworkX
        origin_name: Nome da origem
        destination_name: Nome do destino
        origin_ip: IP de origem
        destination_ip: IP de destino
        filtered_count: Número de medições filtradas
        total_measurements: Total de medições no arquivo original
    
    Returns:
        Caminho do arquivo criado
    """
    filepath = os.path.join(base_path, 'network_analysis_report.txt')
    
    # Calcula estatísticas de latência por caminho
    latency_stats = {}
    for path_id, measurements in measurements_by_path.items():
        latencies = []
        for entry in measurements:
            latency = extract_rtt_from_hops(entry.get('val', []))
            if latency is not None:
                latencies.append(latency)
        
        if latencies:
            latency_stats[path_id] = {
                'count': len(latencies),
                'min': min(latencies),
                'max': max(latencies),
                'avg': sum(latencies) / len(latencies)
            }
    
    # Encontra caminhos no grafo
    shortest_path = None
    all_graph_paths = []
    try:
        shortest_path = nx.shortest_path(G, origin_ip, destination_ip)
        all_graph_paths = find_all_simple_paths(G, origin_ip, destination_ip)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        pass
    
    # Escreve o relatório
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DE REDE\n")
        f.write("="*80 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Origem: {origin_name} ({origin_ip})\n")
        f.write(f"Destino: {destination_name} ({destination_ip})\n")
        f.write("="*80 + "\n\n")
        
        # ESTATÍSTICAS DE FILTRAGEM
        f.write("ESTATÍSTICAS DE FILTRAGEM\n")
        f.write("-"*80 + "\n")
        f.write(f"Total de medições no arquivo: {total_measurements}\n")
        f.write(f"Medições filtradas (não terminam em {destination_ip}): {filtered_count}\n")
        valid_measurements = sum(len(m) for m in measurements_by_path.values())
        f.write(f"Medições válidas (terminam em {destination_ip}): {valid_measurements}\n")
        f.write(f"Taxa de aproveitamento: {(valid_measurements/total_measurements*100):.2f}%\n\n")
        
        # ESTATÍSTICAS DO GRAFO
        f.write("ESTATÍSTICAS DA TOPOLOGIA\n")
        f.write("-"*80 + "\n")
        f.write(f"Número de nós (IPs únicos): {len(G.nodes())}\n")
        f.write(f"Número de arestas (links): {len(G.edges())}\n")
        f.write(f"Grau médio: {sum(dict(G.degree()).values()) / len(G.nodes()):.2f}\n")
        f.write(f"Densidade: {nx.density(G):.4f}\n")
        f.write(f"Grafo conectado: {'Sim' if nx.is_connected(G) else 'Não'}\n")
        
        if nx.is_connected(G):
            f.write(f"Diâmetro da rede: {nx.diameter(G)}\n")
            f.write(f"Raio da rede: {nx.radius(G)}\n")
        
        # CAMINHOS OBSERVADOS VS CAMINHOS POSSÍVEIS
        f.write("\n" + "="*80 + "\n")
        f.write("ANÁLISE DE CAMINHOS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Caminhos OBSERVADOS (medidos): {len(measurements_by_path)}\n")
        f.write(f"Caminhos POSSÍVEIS (no grafo): {len(all_graph_paths)}\n\n")
        
        f.write("DIFERENÇA ENTRE CAMINHOS OBSERVADOS E POSSÍVEIS:\n")
        f.write("-"*80 + "\n")
        f.write("• Caminhos observados: sequências EXATAS de IPs medidas pelo traceroute\n")
        f.write("• Caminhos possíveis: todas as rotas simples entre origem e destino\n")
        f.write("  considerando a topologia construída (sem repetir nós)\n")
        f.write("• Os números diferem porque:\n")
        f.write("  - Traceroute mede caminhos reais em momentos específicos\n")
        f.write("  - O grafo representa todas as conexões vistas ao longo do tempo\n")
        f.write("  - Alguns caminhos possíveis no grafo podem nunca ter sido medidos\n")
        f.write("  - Roteamento dinâmico pode usar sempre os mesmos caminhos\n\n")
        
        # CAMINHO MAIS CURTO
        if shortest_path:
            f.write("CAMINHO MAIS CURTO (GRAFO):\n")
            f.write("-"*80 + "\n")
            f.write(f"Número de saltos: {len(shortest_path) - 1}\n")
            f.write(f"Caminho: {' → '.join(shortest_path)}\n\n")
        else:
            f.write("⚠ Nenhum caminho encontrado no grafo entre origem e destino\n\n")
        
        # CAMINHOS OBSERVADOS DETALHADOS
        f.write("="*80 + "\n")
        f.write("CAMINHOS OBSERVADOS DETALHADOS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Total de medições válidas: {valid_measurements}\n\n")
        
        for path_id in sorted(path_to_nodes.keys()):
            nodes = path_to_nodes[path_id]
            num_measurements = len(measurements_by_path[path_id])
            
            f.write(f"Caminho {path_id} ({len(nodes) - 1} saltos, {num_measurements} medições):\n")
            f.write(f"  {' → '.join(nodes)}\n")
            
            if path_id in latency_stats:
                stats = latency_stats[path_id]
                f.write(f"  Latência: mín={stats['min']:.2f}ms, "
                       f"máx={stats['max']:.2f}ms, média={stats['avg']:.2f}ms\n")
            f.write("\n")
        
        # LISTA DE TODOS OS NÓS
        f.write("="*80 + "\n")
        f.write("LISTA DE NÓS (IPs ÚNICOS)\n")
        f.write("="*80 + "\n")
        for idx, node in enumerate(sorted(G.nodes()), 1):
            degree = G.degree(node)
            f.write(f"{idx:3d}. {node:20s} (grau: {degree})\n")
    
    return filepath


def visualize_graph(G, base_path, origin_ip, destination_ip, path_to_nodes):
    """
    Cria visualização do grafo e salva em arquivo.
    
    Args:
        G: Grafo NetworkX
        base_path: Diretório de saída
        origin_ip: IP de origem
        destination_ip: IP de destino
        path_to_nodes: Mapeamento path_id -> lista de IPs
    
    Returns:
        Caminho do arquivo de imagem salvo
    """
    plt.figure(figsize=(16, 10))
    
    # Layout do grafo
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        pos = nx.shell_layout(G)
    
    # Configuração de cores
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node == origin_ip:
            node_colors.append('#00ff00')
            node_sizes.append(800)
        elif node == destination_ip:
            node_colors.append('#ff0000')
            node_sizes.append(800)
        else:
            node_colors.append('#87ceeb')
            node_sizes.append(500)
    
    # Desenha arestas
    nx.draw_networkx_edges(G, pos, edge_color='#cccccc', 
                          width=1.5, alpha=0.6)
    
    # Destaca caminho mais curto se existir
    try:
        shortest_path = nx.shortest_path(G, origin_ip, destination_ip)
        path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                              edge_color='#ff6b6b', width=3.5, alpha=0.8)
    except:
        pass
    
    # Desenha nós
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='black', linewidths=2)
    
    # Labels
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8,
                           font_weight='bold', font_color='black')
    
    # Título
    title = f"Topologia de Rede - {len(G.nodes())} nós, {len(G.edges())} arestas"
    title += f"\nOrigem: {origin_ip} | Destino: {destination_ip}"
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # Legenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Origem',
                  markerfacecolor='#00ff00', markersize=12, markeredgecolor='black'),
        plt.Line2D([0], [0], marker='o', color='w', label='Destino',
                  markerfacecolor='#ff0000', markersize=12, markeredgecolor='black'),
        plt.Line2D([0], [0], marker='o', color='w', label='Roteador',
                  markerfacecolor='#87ceeb', markersize=10, markeredgecolor='black'),
        plt.Line2D([0], [0], color='#ff6b6b', linewidth=3, 
                  label='Caminho mais curto')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    # Salva
    image_path = os.path.join(base_path, 'network_topology.png')
    plt.savefig(image_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return image_path


def print_summary(base_path, files_created, measurements_by_path, filtered_count, total_measurements):
    """
    Imprime resumo dos arquivos criados.
    """
    print(f"\n{'='*80}")
    print("✓ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
    print(f"{'='*80}")
    print(f"Diretório: {base_path}\n")
    
    valid_measurements = sum(len(m) for m in measurements_by_path.values())
    
    print(f"Total de medições no arquivo: {total_measurements}")
    print(f"Medições filtradas (destino incorreto): {filtered_count}")
    print(f"Medições válidas processadas: {valid_measurements}")
    print(f"Taxa de aproveitamento: {(valid_measurements/total_measurements*100):.2f}%\n")
    
    print(f"Caminhos únicos identificados: {len(measurements_by_path)}\n")
    
    print("Arquivos criados:")
    for file_type, filepath in files_created.items():
        if isinstance(filepath, list):
            print(f"  • {file_type}: {len(filepath)} arquivos")
        else:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            print(f"  • {file_type}: {filename} ({filesize:,} bytes)")
    
    print(f"\n{'='*80}\n")


def main():
    # Configurações
    origin_name = 'rj'
    origin_ip = "200.159.254.238"
    
    destination_name = 'pi'
    destination_ip = "200.137.160.129"
    
    filepath = f'dataset/Train/traceroute/{origin_name}/measure-traceroute_ref-{origin_name}_pop-{destination_name}.json'
    
    # Cria diretórios
    base_path, paths_path = create_output_directories(origin_name, destination_name)
    print(f"✓ Diretórios criados: {base_path}")
    
    # Carrega dados
    print(f"\n📂 Carregando dados de: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        traceroute_data = json.load(f)
    
    total_measurements = len(traceroute_data)
    print(f"✓ Total de medições carregadas: {total_measurements}")
    
    # Processa dados
    print(f"\n📊 Processando dados de traceroute...")
    print(f"🎯 Filtrando apenas caminhos que terminam em: {origin_ip}")
    measurements_by_path, path_to_nodes, G, filtered_count = process_traceroute_data(
        traceroute_data, origin_ip
    )
    
    valid_measurements = sum(len(m) for m in measurements_by_path.values())
    
    print(f"✓ Medições válidas: {valid_measurements}/{total_measurements} ({(valid_measurements/total_measurements*100):.2f}%)")
    print(f"✓ Medições filtradas: {filtered_count}")
    print(f"✓ Caminhos únicos identificados: {len(measurements_by_path)}")
    print(f"✓ Nós no grafo: {len(G.nodes())}")
    print(f"✓ Arestas no grafo: {len(G.edges())}")
    
    # Exporta arquivos
    print(f"\n💾 Exportando arquivos...")
    
    files_created = {}
    path_files_json = []
    path_files_ts = []
    
    # 1. Exporta medições e séries temporais por caminho
    for path_id in sorted(measurements_by_path.keys()):
        measurements = measurements_by_path[path_id]
        
        # JSON com medições completas
        json_file = export_path_measurements_json(paths_path, path_id, measurements)
        path_files_json.append(json_file)
        
        # Série temporal
        ts_file = export_path_timeseries(paths_path, path_id, measurements)
        path_files_ts.append(ts_file)
    
    files_created['Medições por caminho (JSON)'] = path_files_json
    files_created['Séries temporais (TXT)'] = path_files_ts
    
    # 2. Exporta relatório consolidado
    report_file = export_consolidated_report(
        base_path, measurements_by_path, path_to_nodes, G, 
        origin_name, destination_name, origin_ip, destination_ip,
        filtered_count, total_measurements
    )
    files_created['Relatório consolidado'] = report_file
    
    # 3. Salva grafo GML
    gml_path = os.path.join(base_path, 'network_topology.gml')
    nx.write_gml(G, gml_path)
    files_created['Grafo (GML)'] = gml_path
    
    # 4. Visualização
    image_path = visualize_graph(G, base_path, origin_ip, destination_ip, path_to_nodes)
    files_created['Visualização'] = image_path
    
    # Resumo final
    print_summary(base_path, files_created, measurements_by_path, filtered_count, total_measurements)


if __name__ == "__main__":
    main()