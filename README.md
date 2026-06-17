# Análise de dados SINASC — DataSUS

Notebook de análise dos microdados de nascidos vivos (SINASC) do DataSUS.

## Pré-requisitos

- Python 3.10+
- Jupyter Notebook ou JupyterLab

## Instalação

```bash
pip install pysus dbfread dbc-to-dbf pandas geopandas
```

## Dados

Os arquivos de microdados **não estão versionados** neste repositório. Baixe o arquivo `.dbc` do SINASC e coloque em `data/`:

1. Acesse o [TabNet/DataSUS](https://datasus.saude.gov.br/) ou use a biblioteca [PySUS](https://github.com/AlertaDengue/PySUS) para download automático.
2. Salve o arquivo como `data/DNSC2024.dbc` (ajuste o ano conforme o dataset utilizado).
3. Execute o notebook — a célula de descompressão gera `data/DNSC2024.dbf` localmente.

## Execução

```bash
jupyter notebook PySUS.ipynb
```
