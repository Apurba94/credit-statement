"""The 14 CRediT (Contributor Roles Taxonomy, ANSI/NISO Z39.104-2022) roles, aliases and renderers."""
import csv
import difflib
import html
import re

ROLES = ["Conceptualization", "Data curation", "Formal analysis", "Funding acquisition", "Investigation",
         "Methodology", "Project administration", "Resources", "Software", "Supervision", "Validation",
         "Visualization", "Writing - original draft", "Writing - review & editing"]
ALIASES = {"idea": "Conceptualization", "ideas": "Conceptualization", "analysis": "Formal analysis",
           "statistics": "Formal analysis", "funding": "Funding acquisition", "experiments": "Investigation",
           "data collection": "Investigation", "methods": "Methodology", "admin": "Project administration",
           "code": "Software", "programming": "Software", "figures": "Visualization", "writing": "Writing - original draft",
           "draft": "Writing - original draft", "original draft": "Writing - original draft", "editing": "Writing - review & editing",
           "review": "Writing - review & editing", "review & editing": "Writing - review & editing", "data": "Data curation"}
DEGREES = {"lead", "equal", "supporting"}


def _key(s):
    return re.sub(r"[^a-z]", "", s.lower())


def normalize_role(name):
    """Map a column header to the official CRediT role (exact, alias or fuzzy match)."""
    k = _key(name)
    for r in ROLES:
        if _key(r) == k:
            return r
    for a, r in ALIASES.items():
        if _key(a) == k:
            return r
    close = difflib.get_close_matches(k, [_key(r) for r in ROLES], n=1, cutoff=0.8)
    if close:
        return next(r for r in ROLES if _key(r) == close[0])
    raise ValueError("unknown CRediT role %r" % name)


def initials(name):
    parts = re.split(r"[\s]+", name.strip())
    out = []
    for p in parts:
        sub = [s for s in p.split("-") if s]
        out.append("-".join(s[0].upper() + "." for s in sub))
    return "".join(out)


def read_matrix(path):
    """CSV: first column 'author', other columns roles; cells: x/yes/1, or lead/equal/supporting; blank = no.
    Returns (authors, {author: {role: degree or ''}})."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    roles = [normalize_role(h) for h in header[1:]]
    authors, contrib = [], {}
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        a = r[0].strip()
        authors.append(a)
        contrib[a] = {}
        for role, cell in zip(roles, r[1:]):
            c = cell.strip().lower()
            if not c or c in ("0", "no", "n", "-"):
                continue
            contrib[a][role] = c if c in DEGREES else ""
    return authors, contrib


def validate(authors, contrib):
    problems = []
    for a in authors:
        if not contrib.get(a):
            problems.append("%s has no contribution" % a)
    used = {r for a in authors for r in contrib.get(a, {})}
    if not used & {"Writing - original draft", "Writing - review & editing"}:
        problems.append("no author has a writing role")
    for role in ROLES:
        leads = [a for a in authors if contrib.get(a, {}).get(role) == "lead"]
        if len(leads) > 1:
            problems.append("%s has several leads (%s); use 'equal' instead" % (role, ", ".join(leads)))
    return problems


def _label(a, degree, use_initials, show_degree):
    n = initials(a) if use_initials else a
    return "%s (%s)" % (n, degree) if show_degree and degree else n


def by_role(authors, contrib, use_initials=True, show_degree=False):
    parts = []
    for role in ROLES:
        names = [_label(a, contrib[a][role], use_initials, show_degree) for a in authors if role in contrib.get(a, {})]
        if names:
            parts.append("%s: %s" % (role, ", ".join(names)))
    return "; ".join(parts) + "."


def by_author(authors, contrib, use_initials=False, show_degree=False):
    lines = []
    for a in authors:
        roles = [r + (" (%s)" % contrib[a][r] if show_degree and contrib[a][r] else "") for r in ROLES if r in contrib.get(a, {})]
        lines.append("%s: %s." % (initials(a) if use_initials else a, ", ".join(roles)))
    return " ".join(lines)


def jats(authors, contrib):
    """JATS 1.3 <contrib> elements with <role vocab="credit"> tags for publisher submission systems."""
    out = ['<contrib-group>']
    for a in authors:
        out.append('  <contrib contrib-type="author">')
        out.append("    <string-name>%s</string-name>" % html.escape(a))
        for r in ROLES:
            if r in contrib.get(a, {}):
                slug = re.sub(r"[^a-z]+", "-", r.lower().replace("&", "")).strip("-")
                deg = contrib[a][r]
                out.append('    <role vocab="credit" vocab-identifier="https://credit.niso.org/" '
                           'vocab-term="%s" vocab-term-identifier="https://credit.niso.org/contributor-roles/%s/"%s>%s</role>' % (
                               html.escape(r), slug, ' degree-contribution="%s"' % deg if deg else "", html.escape(r)))
        out.append("  </contrib>")
    out.append("</contrib-group>")
    return "\n".join(out) + "\n"
