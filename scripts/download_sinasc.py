#!/usr/bin/env python3
"""Download microdados SINASC (DN) por UF e ano.

- 2017-2022: via PySUS (salva Parquet em data/parquet/)
- 2023-2024: via portal DATASUS + FTP (salva .dbc em data/raw/)

Portal: https://datasus.saude.gov.br/transferencia-de-arquivos/
"""

from __future__ import annotations

import argparse
import ftplib
import json
import shutil
import sys
from pathlib import Path

import pysus
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PARQUET = PROJECT_ROOT / "data" / "parquet"

PYSUS_YEARS = range(2017, 2023)
PORTAL_YEARS = range(2023, 2025)

PORTAL_URL = "https://datasus.saude.gov.br/wp-content/ftp.php"
FTP_HOST = "ftp.datasus.gov.br"
FTP_LEGACY_PATH = "/dissemin/publicos/SINASC/NOV/DNRES"


def _portal_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://datasus.saude.gov.br/transferencia-de-arquivos/",
        "X-Requested-With": "XMLHttpRequest",
    }


def query_portal(uf: str, year: int) -> dict:
    """Consulta ftp.php do portal DATASUS e retorna metadados do arquivo."""
    payload = {
        "tipo_arquivo[]": "DN",
        "modalidade[]": "1",
        "fonte[]": "SINASC",
        "ano[]": str(year),
        "uf[]": uf.upper(),
    }
    response = requests.post(
        PORTAL_URL,
        data=payload,
        headers=_portal_headers(),
        timeout=60,
    )
    response.raise_for_status()
    files = json.loads(response.text)
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo SINASC encontrado no portal para {uf}/{year}."
        )
    return files[0]


def download_ftp(remote_path: str, destination: Path) -> None:
    """Baixa um arquivo do FTP do DATASUS."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"  [ok] já existe: {destination.name}")
        return

    print(f"  baixando {destination.name} ...")
    with ftplib.FTP(FTP_HOST, timeout=120) as ftp:
        ftp.login()
        with destination.open("wb") as handle:
            ftp.retrbinary(f"RETR {remote_path}", handle.write)


def download_portal_year(uf: str, year: int, output_dir: Path) -> Path:
    """Baixa .dbc de 2023+ usando a API do portal de transferência."""
    meta = query_portal(uf, year)
    filename = meta["arquivo"]
    remote_path = meta["endereco"].replace(f"ftp://{FTP_HOST}", "")
    destination = output_dir / filename.lower()
    download_ftp(remote_path, destination)
    return destination


def download_pysus_year(uf: str, year: int, output_dir: Path) -> Path:
    """Baixa via PySUS e copia o Parquet para data/parquet/."""
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = output_dir / f"DN{uf.upper()}{year}.parquet"

    if expected.exists() and expected.stat().st_size > 0:
        print(f"  [ok] já existe: {expected.name}")
        return expected

    print(f"  baixando DN{uf.upper()}{year} via PySUS ...")
    paths = pysus.sinasc(state=uf.upper(), year=year, show_progress=True)
    if not paths:
        raise FileNotFoundError(f"PySUS não retornou arquivos para {uf}/{year}.")

    source = Path(paths[0])
    shutil.copy2(source, expected)
    return expected


def download_years(
    uf: str,
    years: list[int],
    raw_dir: Path = DATA_RAW,
    parquet_dir: Path = DATA_PARQUET,
) -> None:
    uf = uf.upper()
    print(f"\nSINASC — UF={uf}, anos={years}\n")

    for year in sorted(years):
        print(f"[{year}]")
        if year in PYSUS_YEARS:
            path = download_pysus_year(uf, year, parquet_dir)
            print(f"  -> {path.relative_to(PROJECT_ROOT)}")
        elif year in PORTAL_YEARS:
            path = download_portal_year(uf, year, raw_dir)
            print(f"  -> {path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  [!] ano {year} fora do escopo configurado (2017-2024)")


def parse_years(value: str) -> list[int]:
    if "-" in value:
        start, end = value.split("-", 1)
        return list(range(int(start), int(end) + 1))
    return [int(y.strip()) for y in value.split(",") if y.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download microdados SINASC (DN).")
    parser.add_argument(
        "--uf",
        default="SC",
        help="Sigla da UF (padrão: SC)",
    )
    parser.add_argument(
        "--years",
        default="2017-2024",
        help="Anos ou intervalo, ex.: 2017-2024 ou 2020,2022",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DATA_RAW,
        help="Destino dos .dbc (2023-2024)",
    )
    parser.add_argument(
        "--parquet-dir",
        type=Path,
        default=DATA_PARQUET,
        help="Destino dos Parquet (2017-2022)",
    )
    args = parser.parse_args(argv)

    try:
        download_years(
            uf=args.uf,
            years=parse_years(args.years),
            raw_dir=args.raw_dir,
            parquet_dir=args.parquet_dir,
        )
    except (requests.RequestException, ftplib.Error, FileNotFoundError) as exc:
        print(f"\nErro: {exc}", file=sys.stderr)
        return 1

    print("\nConcluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
