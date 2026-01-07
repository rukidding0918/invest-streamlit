from typing import Literal
from .base import DataLoader
from .fdr_loader import FdrLoader
from .krx_loader import PyKrxLoader

def get_loader(source: Literal["fdr", "pykrx"] = "fdr") -> DataLoader:
    if source == "fdr":
        return FdrLoader()
    elif source == "pykrx":
        return PyKrxLoader()
    else:
        raise ValueError(f"Unknown source: {source}")

__all__ = ["get_loader", "DataLoader", "FdrLoader", "PyKrxLoader"]
