import pandas as pd
import numpy as np
from io import StringIO

def perform_interpolation(filepath):
    df = pd.read_csv(filepath)
    print(df)

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Define a coluna 'timestamp' como o índice do DataFrame
    # O 'pandas' agora entenderá que a distância entre as linhas é temporal
    df_indexed = df.set_index('timestamp')

    print("--- DataFrame Indexado (Pronto para Interpolação) ---")
    print(df_indexed)

    # Aplica a interpolação linear, tratando cada coluna (caminho) separadamente
    # O 'limit_direction='both'' garante que a interpolação ocorra para frente e para trás
    df_interpolated = df_indexed.interpolate(method='linear', limit_direction='both')

    print("\n--- DataFrame com Interpolação Linear Completa ---")
    print(df_interpolated)

    return df_interpolated

    # Exemplo de Outro Método (LOCF - Last Observation Carried Forward) --> Mesmo resultado que o anterior, para rj-es
    # df_interpolated_locf = df_indexed.fillna(method='ffill').fillna(method='bfill')
    # print("\n--- DataFrame com Interpolação LOCF ---")
    # print(df_interpolated_locf)


def save_interpolation(filepath, df_interpolated):
    # 1. Reseta o índice para que a coluna 'timestamp' volte a ser uma coluna normal
    df_final = df_interpolated.reset_index()

    # 2. Converte a coluna datetime ('timestamp') de volta para Unix Timestamp (em segundos)
    # O .astype(int) realiza a conversão para nanosegundos (padrão do pandas)
    # Dividimos por 10^9 para converter de nanosegundos para segundos.
    df_final['timestamp'] = (df_final['timestamp'].astype(np.int64) // 10**9)

    # Opcional: converte para o tipo de dado inteiro padrão (int32 ou int64)
    df_final['timestamp'] = df_final['timestamp'].astype(pd.Int64Dtype())

    print("\n--- DataFrame Final (Timestamp em segundos) ---")
    print(df_final)

    df_final.to_csv(filepath, index=False)

    print(f"\nSucesso! O arquivo '{filepath}' foi salvo.")

def main():
    filepath_in = 'analysis/rj/rj-es/latency_matrix.csv'
    filepath_out = 'analysis/rj/rj-es/latency_matrix_interpolated.csv'

    df_interpolated = perform_interpolation(filepath_in)
    save_interpolation(filepath_out, df_interpolated)



if __name__ == "__main__":
    main()