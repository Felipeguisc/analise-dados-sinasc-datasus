# Análise de dados SINASC — DataSUS

Notebook e scripts para análise dos microdados de nascidos vivos (SINASC) do [DataSUS](https://datasus.saude.gov.br/).

## Estrutura

```
data/
  parquet/     # 2017-2022 (via PySUS)
  raw/         # 2023-2024 (.dbc via portal DATASUS)
scripts/
  download_sinasc.py   # download automatizado
  load_sinasc.py       # leitura unificada Parquet/DBC
PySUS.ipynb            # análise exploratória
```

## Pré-requisitos

- Python 3.10+
- Jupyter Notebook ou JupyterLab

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Download dos dados

Os microdados **não são versionados** neste repositório. A estratégia de download varia por ano:

| Período   | Fonte | Formato | Método |
|-----------|-------|---------|--------|
| 2017–2022 | FTP clássico (`NOV/DNRES`) | Parquet | PySUS |
| 2023–2024 | Portal + FTP (`1996_/Dados/DNRES`) | `.dbc` | API do portal |

### Automático (recomendado)

```bash
# Santa Catarina, todos os anos (padrão)
python scripts/download_sinasc.py

# Outra UF ou intervalo
python scripts/download_sinasc.py --uf SP --years 2017-2024
python scripts/download_sinasc.py --uf SC --years 2023,2024
```

O script detecta o ano e escolhe o método correto. Para 2023–2024, consulta a [Transferência de Arquivos](https://datasus.saude.gov.br/transferencia-de-arquivos/) e baixa via FTP interno — **funciona em código**, sem passo a passo manual.

### Manual (2023–2024, se preferir)

1. Acesse [Transferência de Arquivos](https://datasus.saude.gov.br/transferencia-de-arquivos/)
2. **Fonte:** SINASC
3. **Modalidade:** Dados
4. **Tipo de Arquivo:** DN — Declarações de nascidos vivos
5. **Ano:** 2023 ou 2024
6. **UF:** desejada (ex.: SC)
7. Clique em **Enviar**, selecione o arquivo e **Download**
8. Salve em `data/raw/` (ex.: `dnsc2024.dbc`)

## Execução

```bash
jupyter notebook PySUS.ipynb
```

## Nomenclatura dos arquivos

Padrão DATASUS: `DN{UF}{AAAA}` — ex.: `DNSC2024` = Santa Catarina, 2024.

## Referências

- [PySUS](https://github.com/AlertaDengue/PySUS)
- [Documentação SINASC](https://brazilvisible.org/docs/apis/saude-datasus/sinasc/)
