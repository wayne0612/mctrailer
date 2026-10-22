import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "mctrailer", "scripts"))

import repo_profile as rp


class TestParse(unittest.TestCase):
    def test_parse_url(self):
        self.assertEqual(rp.parse_repo_url("https://github.com/psf/requests"), ("psf", "requests"))
        self.assertEqual(rp.parse_repo_url("https://github.com/vuejs/vue.git"), ("vuejs", "vue"))

    def test_parse_bad(self):
        with self.assertRaises(ValueError):
            rp.parse_repo_url("not-a-url")


class TestClassify(unittest.TestCase):
    def test_each_genre(self):
        self.assertEqual(rp.classify_genre("fix a nasty bug", "Python", ["hotfix"]), rp.GENRE_FIX)
        self.assertEqual(rp.classify_genre("v2 release deploy", "Go", ["changelog"]), rp.GENRE_RELEASE)
        self.assertEqual(rp.classify_genre("big refactor of architecture", "TS", ["migrate"]), rp.GENRE_REFACTOR)
        self.assertEqual(rp.classify_genre("my weekend toy project", "JS"), rp.GENRE_SIDE)

    def test_default_and_empty(self):
        self.assertEqual(rp.classify_genre(""), rp.GENRE_SIDE)
        self.assertEqual(rp.classify_genre("hello world library"), rp.GENRE_SIDE)

    def test_deterministic(self):
        args = ("refactor performance rewrite", "Rust", ["optimize"], ["chore: cleanup"])
        self.assertEqual(rp.classify_genre(*args), rp.classify_genre(*args))

    def test_protagonist(self):
        self.assertEqual(rp.protagonist_for("Python"), "数据法师")
        self.assertEqual(rp.protagonist_for("Rust"), "系统工匠")
        self.assertEqual(rp.protagonist_for(None), "独立开发者")


class TestProfile(unittest.TestCase):
    def test_profile_from_payload(self):
        p = rp.profile_from_payload(
            {"name": "x", "description": "fix bug", "language": "Python",
             "stargazers_count": 1500, "topics": ["hotfix"]},
            ["fix: crash"])
        self.assertEqual(p["genre"], rp.GENRE_FIX)
        self.assertEqual(p["protagonist"], "数据法师")
        self.assertEqual(p["stars"], 1500)
        self.assertEqual(p["source"], "github-live")

    def test_degraded(self):
        d = rp.degraded_profile("https://github.com/a/b")
        self.assertEqual(d["source"], "offline-degraded")
        self.assertEqual(d["genre"], rp.GENRE_SIDE)


if __name__ == "__main__":
    unittest.main()
