import pandas as pd

# Carregamento dos arquivos CSV
df_origem = pd.read_csv(r'C:\Users\Karol\Downloads\teste_bi-main\teste_etl\origem.csv')
df_municipios = pd.read_csv(r'C:\Users\Karol\Downloads\teste_bi-main\teste_etl\dimensoes\d_municipio.csv')
df_tempo = pd.read_csv(r'C:\Users\Karol\Downloads\teste_bi-main\teste_etl\dimensoes\d_tempo.csv')

# Renomeação das colunas do DataFrame de municípios para facilitar o merge
df_municipios.rename(columns={'dmun_codibge': 'codigo_ibge', 'dmun_municipiox': 'nome_municipio'}, inplace=True)

# Verificação dos códigos de município estão no mesmo tipo e normalização
df_origem['co_municipio_residencia_atual'] = df_origem['co_municipio_residencia_atual'].astype(str).str.split('.').str[0]  # Remove o '.0'
df_municipios['codigo_ibge'] = df_municipios['codigo_ibge'].astype(str).str.strip()

# Converção da coluna de data para datetime
df_origem['dt_diagnostico_sintoma'] = pd.to_datetime(df_origem['dt_diagnostico_sintoma'], errors='coerce')

# Mapeamento dos valores numéricos para suas descrições textuais
map_tp_entrada = {
    1: 'Caso novo',
    2: 'Recidiva',
    3: 'Reingresso após abandono',
    4: 'Pós-óbito',
    5: 'Transferência',
    6: 'Desconhecido'
}

map_tp_forma = {
    1: 'Pulmonar',
    2: 'Extrapulmonar',
    3: 'Pulmonar + extrapulmonar'
}

map_tp_situacao_encerramento = {
    1: 'Cura',
    2: 'Abandono',
    3: 'Óbito por tuberculose',
    4: 'Óbito por outras causas',
    5: 'Transferência',
    6: 'Mudança de Diagnóstico',
    7: 'Tuberculose Multirresistente',
    8: 'Óbito por tuberculose multirresistente',
    9: 'Falência de tratamento',
    10: 'Outros'
}

# Aplicação dos mapeamentos
df_origem['tp_entrada'] = df_origem['tp_entrada'].map(map_tp_entrada)
df_origem['tp_forma'] = df_origem['tp_forma'].map(map_tp_forma)
df_origem['tp_situacao_encerramento'] = df_origem['tp_situacao_encerramento'].map(map_tp_situacao_encerramento)

# Filtragem dos dados conforme os critérios especificados
df_filtered = df_origem[
    ((df_origem['tp_entrada'] == 'Caso novo') |
     (df_origem['tp_entrada'] == 'Pós-óbito') |
     (df_origem['tp_entrada'].isna())) &  # Tipo de entrada desconhecido
    ((df_origem['tp_forma'] == 'Pulmonar') |
     (df_origem['tp_forma'] == 'Pulmonar + extrapulmonar')) &
    (df_origem['tp_situacao_encerramento'] != 'Mudança de Diagnóstico') &
    (df_origem['dt_diagnostico_sintoma'] >= '2021-01-01')  # Dados a partir de 2021
]

print("Dados após filtragem:")
print(df_filtered.head())

# Verificação de correspondência dos códigos antes de mesclar
print("Códigos de municípios na origem sem correspondência:", set(df_filtered['co_municipio_residencia_atual']) - set(df_municipios['codigo_ibge']))

# Mesclagem com o DataFrame de municípios para obter o nome completo dos municípios
df_filtered = df_filtered.merge(df_municipios[['codigo_ibge', 'nome_municipio']],
                                left_on='co_municipio_residencia_atual',
                                right_on='codigo_ibge',
                                how='left')

print("Dados após mesclagem com municípios:")
print(df_filtered.head())
