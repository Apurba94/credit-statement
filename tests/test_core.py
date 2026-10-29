import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from credit_statement.cli import main
from credit_statement.core import by_author, by_role, initials, jats, normalize_role, read_matrix, validate

CSV = """author,Conceptualisation,code,Formal Analysis,Writing - original draft,review & editing,Supervision
Ana Silva,lead,x,x,lead,x,
Jean-Paul Martin,equal,,supporting,,x,
Bo Chen,,,,,x,lead
"""


def load(text=CSV):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "m.csv")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class RoleTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_role("Conceptualisation"), "Conceptualization")     # UK spelling via fuzzy match
        self.assertEqual(normalize_role("code"), "Software")
        self.assertEqual(normalize_role("WRITING – REVIEW & EDITING"), "Writing - review & editing")
        with self.assertRaises(ValueError):
            normalize_role("coffee")

    def test_initials(self):
        self.assertEqual(initials("Jean-Paul Martin"), "J.-P.M.")
        self.assertEqual(initials("Ana Silva"), "A.S.")


class StatementTests(unittest.TestCase):
    def setUp(self):
        self.authors, self.contrib = read_matrix(load())

    def test_by_role(self):
        s = by_role(self.authors, self.contrib)
        self.assertTrue(s.startswith("Conceptualization: A.S., J.-P.M.; Formal analysis: A.S., J.-P.M.;"))
        self.assertIn("Software: A.S.", s)
        self.assertIn("Supervision: B.C.", s)
        self.assertIn("Conceptualization: A.S. (lead), J.-P.M. (equal)", by_role(self.authors, self.contrib, show_degree=True))

    def test_by_author_and_jats(self):
        self.assertIn("Bo Chen: Supervision, Writing - review & editing.", by_author(self.authors, self.contrib))
        x = jats(self.authors, self.contrib)
        self.assertIn('vocab-term="Writing - review &amp; editing"', x)
        self.assertIn("contributor-roles/writing-review-editing/", x)
        self.assertIn('degree-contribution="lead"', x)

    def test_validation(self):
        self.assertEqual(validate(self.authors, self.contrib), [])
        a, c = read_matrix(load("author,Software,Supervision\nX,lead,\nY,lead,\nZ,,\n"))
        p = " ".join(validate(a, c))
        self.assertIn("Z has no contribution", p)
        self.assertIn("no author has a writing role", p)
        self.assertIn("several leads", p)

    def test_cli(self):
        with redirect_stdout(io.StringIO()) as buf, redirect_stderr(io.StringIO()):
            main([load(), "--full-names"])
            main(["--template"])
        self.assertIn("Software: Ana Silva", buf.getvalue())
        self.assertIn("author,Conceptualization,Data curation", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
