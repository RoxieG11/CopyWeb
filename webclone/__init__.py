"""WebClone v2.0 - Web sitelerini yerel klasöre kopyalama, anonim tarama ve istihbarat aracı."""
from .core import CloneOptions, CloneResult, Cloner
from .recon import ReconCollector, ReconReport
from .stealth import StealthManager

__all__ = ["Cloner", "CloneOptions", "CloneResult", "ReconCollector", "ReconReport", "StealthManager"]
__version__ = "2.0.0"
