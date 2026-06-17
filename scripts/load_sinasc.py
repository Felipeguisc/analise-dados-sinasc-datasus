"""Utilitários para carregar microdados SINASC a partir de Parquet ou DBC."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from dbctodbf import DBCDecompress
from dbfread import DBF


def load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_dbc(path: Path, encoding: str = "iso-8859-1") -> pd.DataFrame:
    dbf_path = path.with_suffix(".dbf")
    if not dbf_path.exists() or dbf_path.stat().st_mtime < path.stat().st_mtime:
        DBCDecompress().decompressFile(str(path), str(dbf_path))
    return pd.DataFrame(iter(DBF(dbf_path, encoding=encoding)))


def _find_file(directory: Path, pattern: str) -> Path | None:
    if not directory.exists():
        return None
    target = pattern.lower()
    for path in directory.iterdir():
        if path.name.lower() == target:
            return path
    return None


def load_year(
    uf: str,
    year: int,
    raw_dir: Path,
    parquet_dir: Path,
    encoding: str = "iso-8859-1",
) -> pd.DataFrame:
    """Carrega um ano de SINASC, detectando Parquet (2017-22) ou DBC (2023-24)."""
    uf = uf.upper()
    stem = f"DN{uf}{year}"
    parquet = _find_file(parquet_dir, f"{stem}.parquet")
    dbc = _find_file(raw_dir, f"{stem}.dbc")

    if parquet:
        return load_parquet(parquet)
    if dbc:
        return load_dbc(dbc, encoding=encoding)

    raise FileNotFoundError(
        f"Dados não encontrados para {uf}/{year}. "
        f"Esperado: {stem}.parquet ou {stem}.dbc"
    )
