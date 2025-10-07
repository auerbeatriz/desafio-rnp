import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import os
from datetime import datetime


def create_output_directory(output_name):
    """
    Cria a estrutura de diretórios para saída.
    
    Args:
        output_name: Nome do diretório de saída
    
    Returns:
        Caminho completo do diretório criado
    """
    output_path = os.path.join('out', '_manual', output_name)
    os.makedirs(output_path, exist_ok=True)
    return output_path


def extract_routes(traceroute_data, G):
    routes = []

    for entry in traceroute_data:
        route = []
        previous_node = None

        for hop in entry['val']:
            current_hop = hop['ip']

            if not current_hop:
                continue
            
            G.add_node(current_hop)

            if previous_node != None:
                G.add_edge(previous_node, current_hop)
            
            previous_node = current_hop
            route.append(previous_node)
        
        if route not in routes: routes.append(route)
    
    return routes


def find_all_paths(G, origin, destination, max_paths=10):
    """
    Encontra todos os caminhos simples entre origem e destino.
    
    Args:
        G: Grafo NetworkX
        origin: Nó de origem
        destination: Nó de destino
        max_paths: Número máximo de caminhos a retornar (padrão: 10)
    
    Returns:
        Lista de caminhos encontrados
    """
    try:
        # Encontra todos os caminhos simples (sem ciclos)
        all_paths = list(nx.all_simple_paths(G, origin, destination))
        
        if not all_paths:
            return []
        
        # Ordena por número de saltos (menor primeiro)
        all_paths.sort(key=len)
        
        return all_paths
        
    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return []


def export_paths_to_file(output_path, origin, destination, all_paths, max_display=20):
    """
    Exporta todos os caminhos para um arquivo de texto.
    
    Args:
        output_path: Diretório de saída
        origin: Nó de origem
        destination: Nó de destino
        all_paths: Lista de caminhos
        max_display: Número máximo de caminhos a exibir em detalhes
    """
    filepath = os.path.join(output_path, 'caminhos.txt')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"TODOS OS CAMINHOS POSSÍVEIS: {origin} → {destination}\n")
        f.write("="*70 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        if not all_paths:
            f.write("❌ Nenhum caminho encontrado!\n")
            return filepath
        
        f.write(f"✓ Total de caminhos encontrados: {len(all_paths)}\n\n")
        
        # Exibe caminhos detalhados
        for idx, path in enumerate(all_paths[:max_display], 1):
            hops = len(path) - 1
            f.write(f"Caminho {idx} ({hops} saltos):\n")
            f.write(f"  {' → '.join(path)}\n\n")
        
        if len(all_paths) > max_display:
            f.write(f"\n... e mais {len(all_paths) - max_display} caminhos\n")
        
        # Resumo estatístico dos caminhos
        f.write("\n" + "="*70 + "\n")
        f.write("ESTATÍSTICAS DOS CAMINHOS\n")
        f.write("="*70 + "\n")
        
        path_lengths = [len(p) - 1 for p in all_paths]
        f.write(f"Caminho mais curto: {min(path_lengths)} saltos\n")
        f.write(f"Caminho mais longo: {max(path_lengths)} saltos\n")
        f.write(f"Média de saltos: {sum(path_lengths) / len(path_lengths):.2f}\n")
        
    return filepath


def export_statistics_to_file(output_path, G, routes, origin, destination, shortest_path):
    """
    Exporta estatísticas do grafo para um arquivo.
    
    Args:
        output_path: Diretório de saída
        G: Grafo NetworkX
        routes: Lista de rotas extraídas
        origin: Nó de origem
        destination: Nó de destino
        shortest_path: Caminho mais curto encontrado
    """
    filepath = os.path.join(output_path, 'estatisticas.txt')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DE REDE\n")
        f.write("="*70 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        # Estatísticas do grafo
        f.write("ESTATÍSTICAS DO GRAFO\n")
        f.write("-"*70 + "\n")
        f.write(f"Número de nós: {len(G.nodes())}\n")
        f.write(f"Número de arestas: {len(G.edges())}\n")
        f.write(f"Grau médio: {sum(dict(G.degree()).values()) / len(G.nodes()):.2f}\n")
        f.write(f"Densidade: {nx.density(G):.4f}\n")
        f.write(f"Conectado: {'Sim' if nx.is_connected(G) else 'Não'}\n")
        
        if nx.is_connected(G):
            f.write(f"Diâmetro: {nx.diameter(G)}\n")
            f.write(f"Raio: {nx.radius(G)}\n")
        
        f.write(f"\nTotal de rotas extraídas: {len(routes)}\n")
        
        # Informações sobre origem e destino
        f.write("\n" + "="*70 + "\n")
        f.write("ANÁLISE DE ROTA\n")
        f.write("="*70 + "\n")
        f.write(f"Origem: {origin}\n")
        f.write(f"Destino: {destination}\n\n")
        
        if shortest_path:
            f.write("CAMINHO MAIS CURTO\n")
            f.write("-"*70 + "\n")
            f.write(f"Número de saltos: {len(shortest_path) - 1}\n")
            f.write(f"Caminho: {' → '.join(shortest_path)}\n")
        else:
            f.write("❌ Nenhum caminho encontrado entre origem e destino\n")
        
        # Lista de todos os nós
        f.write("\n" + "="*70 + "\n")
        f.write("LISTA DE NÓS (IPs)\n")
        f.write("="*70 + "\n")
        for idx, node in enumerate(sorted(G.nodes()), 1):
            degree = G.degree(node)
            f.write(f"{idx:3d}. {node} (grau: {degree})\n")
    
    return filepath


def visualize_graph(G, output_path, origin=None, destination=None, paths=None):
    """
    Cria uma visualização melhorada do grafo e salva em arquivo.
    
    Args:
        G: Grafo NetworkX
        output_path: Diretório de saída
        origin: Nó de origem (opcional)
        destination: Nó de destino (opcional)
        paths: Lista de caminhos para destacar (opcional)
    
    Returns:
        Caminho do arquivo de imagem salvo
    """
    plt.figure(figsize=(16, 10))
    
    # Layout do grafo (hierárquico se possível)
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        pos = nx.shell_layout(G)
    
    # Configuração de cores
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node == origin:
            node_colors.append('#00ff00')  # Verde para origem
            node_sizes.append(800)
        elif node == destination:
            node_colors.append('#ff0000')  # Vermelho para destino
            node_sizes.append(800)
        else:
            node_colors.append('#87ceeb')  # Azul claro para outros
            node_sizes.append(500)
    
    # Desenha as arestas (cinza claro)
    nx.draw_networkx_edges(G, pos, edge_color='#cccccc', 
                          width=1.5, alpha=0.6)
    
    # Se houver caminhos, destaca o caminho mais curto
    if paths and len(paths) > 0:
        shortest_path = paths[0]
        path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                              edge_color='#ff6b6b', width=3.5, 
                              alpha=0.8, style='solid')
    
    # Desenha os nós
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='black', linewidths=2)
    
    # Labels dos nós (IPs)
    labels = {node: node for node in G.nodes()}  # Apenas último octeto
    nx.draw_networkx_labels(G, pos, labels, font_size=9,
                           font_weight='bold', font_color='black')
    
    # Título e informações
    title = f"Topologia de Rede - {len(G.nodes())} nós, {len(G.edges())} arestas"
    if origin and destination:
        title += f"\nOrigem: {origin} | Destino: {destination}"
    
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
    ]
    
    if paths and len(paths) > 0:
        legend_elements.append(
            plt.Line2D([0], [0], color='#ff6b6b', linewidth=3, 
                      label='Caminho mais curto')
        )
    
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    # Salva a imagem
    image_path = os.path.join(output_path, 'grafo.png')
    plt.savefig(image_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return image_path


def print_summary(output_path, files_created):
    """
    Imprime resumo dos arquivos criados.
    
    Args:
        output_path: Diretório de saída
        files_created: Dicionário com os arquivos criados
    """
    print(f"\n{'='*70}")
    print("✓ ARQUIVOS EXPORTADOS COM SUCESSO")
    print(f"{'='*70}")
    print(f"Diretório: {output_path}\n")
    
    for file_type, filepath in files_created.items():
        filename = os.path.basename(filepath)
        print(f"  • {file_type}: {filename}")
    
    print(f"\n{'='*70}\n")


def main():
    # Configurações
    filepath = 'dataset/Train/traceroute/rj/measure-traceroute_ref-rj_pop-pi.json'
    output_name = 'rj-pi'  # ← ALTERE AQUI O NOME DA PASTA DE SAÍDA
    origin = "200.137.160.129"
    destination = "200.159.254.238"
    
    # Cria diretório de saída
    output_path = create_output_directory(output_name)
    print(f"✓ Diretório criado: {output_path}")
    
    # Carrega dados e cria grafo
    G = nx.Graph()
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n📊 Extraindo rotas do traceroute...")
    routes = extract_routes(data, G)
    print(f"✓ Total de rotas extraídas: {len(routes)}")
    
    # Encontra caminho mais curto
    shortest_path = None
    try:
        shortest_path = nx.shortest_path(G, origin, destination)
        print(f"\n✓ Caminho mais curto: {len(shortest_path) - 1} saltos")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        print(f"\n❌ Nenhum caminho encontrado entre origem e destino")
    
    # Encontra todos os caminhos possíveis
    print(f"\n🔍 Buscando todos os caminhos possíveis...")
    all_paths = find_all_paths(G, origin, destination, max_paths=100)
    
    if all_paths:
        print(f"✓ Total de caminhos encontrados: {len(all_paths)}")
    else:
        print(f"❌ Nenhum caminho encontrado")
    
    # Exporta arquivos
    print(f"\n💾 Exportando arquivos...")
    
    files_created = {}
    
    # 1. Salva o grafo GML
    gml_path = os.path.join(output_path, 'topologia.gml')
    nx.write_gml(G, gml_path)
    files_created['Grafo GML'] = gml_path
    
    # 2. Exporta estatísticas
    stats_path = export_statistics_to_file(output_path, G, routes, origin, 
                                           destination, shortest_path)
    files_created['Estatísticas'] = stats_path
    
    # 3. Exporta caminhos
    paths_path = export_paths_to_file(output_path, origin, destination, 
                                      all_paths, max_display=50)
    files_created['Caminhos'] = paths_path
    
    # 4. Gera e salva visualização
    image_path = visualize_graph(G, output_path, origin, destination, 
                                 all_paths if all_paths else None)
    files_created['Imagem do Grafo'] = image_path
    
    # Resumo final
    print_summary(output_path, files_created)


if __name__ == "__main__":
    main()