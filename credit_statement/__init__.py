"""Generate CRediT author-contribution statements from a contribution matrix."""
from .core import ROLES, normalize_role, read_matrix, by_role, by_author, jats, validate, initials

__version__ = "0.1.0"
__all__ = ["ROLES", "normalize_role", "read_matrix", "by_role", "by_author", "jats", "validate", "initials"]
