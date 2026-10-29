"""Command-line interface for credit-statement."""
import argparse
import sys

from .core import ROLES, by_author, by_role, jats, read_matrix, validate


def main(argv=None):
    ap = argparse.ArgumentParser(prog="credit-statement", description="CRediT author contribution statements.")
    ap.add_argument("matrix", nargs="?", help="CSV: author column + one column per role")
    ap.add_argument("-f", "--format", choices=["by-role", "by-author", "jats"], default="by-role")
    ap.add_argument("--full-names", action="store_true", help="names instead of initials (by-role)")
    ap.add_argument("--degree", action="store_true", help="show lead/equal/supporting")
    ap.add_argument("--template", action="store_true", help="print an empty CSV template and exit")
    args = ap.parse_args(argv)
    if args.template:
        print("author," + ",".join(ROLES))
        return 0
    if not args.matrix:
        ap.error("matrix CSV is required")
    try:
        authors, contrib = read_matrix(args.matrix)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    for p in validate(authors, contrib):
        print("warning: " + p, file=sys.stderr)
    if args.format == "jats":
        sys.stdout.write(jats(authors, contrib))
    elif args.format == "by-author":
        print(by_author(authors, contrib, show_degree=args.degree))
    else:
        print("**Author contributions (CRediT):** " + by_role(authors, contrib, not args.full_names, args.degree))
    return 0
