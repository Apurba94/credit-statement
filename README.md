# credit-statement

**Turn a simple spreadsheet of who did what into a correct CRediT author contribution statement,
grouped by role or by author, or as JATS XML for submission systems.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Most journals now require contribution statements using the CRediT taxonomy (14 standard roles,
ANSI/NISO Z39.104-2022). Writing them by hand for many authors is tedious, role names get misspelt,
and some authors end up with no listed contribution. A contribution matrix maintained during the project
is also a good basis for authorship discussions.

## Features

- Matrix CSV: one row per author, one column per role; cells `x`, `lead`, `equal`, `supporting` or blank
- Role headers normalized to official CRediT names (aliases like `code`, `statistics`, `review & editing`,
  British spellings, fuzzy matching)
- Output by role with initials (`Conceptualization: A.S., J.-P.M.; ...`), by author, optional degree of
  contribution, or JATS 1.3 `<role vocab="credit">` XML
- Checks: authors without contributions, no writing role, several leads for one role
- `--template` prints an empty matrix with all 14 roles

## Usage

```bash
pip install .
credit-statement --template > contributions.csv          # fill it in with co-authors
credit-statement contributions.csv
credit-statement contributions.csv -f by-author --degree
credit-statement contributions.csv -f jats > contrib.xml
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
