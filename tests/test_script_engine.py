import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "mctrailer", "scripts"))

import repo_profile as rp
import script_engine as se


def _profile(name, desc, lang, stars, topics, commits):
    genre = rp.classify_genre(desc, lang, topics, commits)
    return rp.profile_from_payload(
        {"name": name, "description": desc, "language": lang,
         "stargazers_count": stars, "topics": topics}, commits)


# 10 fixed samples: the plan requires consistent input -> consistent output.
SAMPLES = [
    _profile("webapp", "fix login bug", "JavaScript", 10, ["bug"], ["fix: crash"]),
    _profile("api", "release v2 deploy pipeline", "Go", 250, ["release"], ["chore: release"]),
    _profile("core", "architecture refactor migrate", "TypeScript", 40000, ["refactor"], ["refactor: split"]),
    _profile("notes", "my personal weekend toy", "Python", 3, ["toy"], ["init"]),
    _profile("lib", "a tiny http helper", "C", 800, [], []),
    _profile("cli", "hotfix panic segfault", "Rust", 5, ["hotfix"], ["fix: segfault"]),
    _profile("site", "ship the new landing page", "HTML", 12, ["launch"], ["feat: launch"]),
    _profile("engine", "optimize performance rewrite", "C++", 9000, ["performance"], ["perf: optimize"]),
    _profile("playground", "learning experiments demo", "Ruby", 1, ["demo"], ["wip"]),
    _profile("tool", "debug traceback flaky test", "Java", 44, ["debug"], ["fix: flaky"]),
]


class TestScriptEngine(unittest.TestCase):
    def test_determinism_all_samples(self):
        for i, p in enumerate(SAMPLES):
            self.assertEqual(se.build_script(p), se.build_script(p), f"sample {i} not deterministic")

    def test_genre_titles(self):
        s_fix = se.build_script(SAMPLES[0])
        self.assertEqual(s_fix["genre"], rp.GENRE_FIX)
        self.assertIn("第 37 次修复", s_fix["film_title"])
        s_rel = se.build_script(SAMPLES[1])
        self.assertIn("部署前 15 分钟", s_rel["film_title"])
        s_ref = se.build_script(SAMPLES[2])
        self.assertIn("重构纪元", s_ref["film_title"])
        s_side = se.build_script(SAMPLES[3])
        self.assertIn("一个人的公路", s_side["film_title"])

    def test_stat_block(self):
        s = se.build_script(SAMPLES[2])  # 40000 stars
        self.assertEqual(s["stat_block"]["stars"], 40000)
        self.assertEqual(s["stat_block"]["stars_phrase"], "40.0k stars")
        s2 = se.build_script(SAMPLES[0])  # 10 stars
        self.assertEqual(s2["stat_block"]["stars_phrase"], "10 stars")

    def test_minimal_profile_no_crash(self):
        s = se.build_script({})
        self.assertTrue(s["film_title"])
        self.assertEqual(s["genre"], rp.GENRE_SIDE)


if __name__ == "__main__":
    unittest.main()
