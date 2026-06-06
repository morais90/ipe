from pathlib import Path

from ipe.cli.console import BloomingTree


class TestBloomingTree:
    def test_starts_with_no_flowers(self):
        tree = BloomingTree(version="0.1.0", target="python", spec_path="x.yaml")

        assert tree._bloom_count() == 0

    def test_bloom_grows_with_elapsed_time(self):
        tree = BloomingTree(version="0.1.0", target="python", spec_path="x.yaml")
        tree._total_start -= 1.6

        assert tree._bloom_count() == 4

    def test_finish_jumps_to_full_bloom(self):
        tree = BloomingTree(version="0.1.0", target="python", spec_path="x.yaml")

        tree.finish()

        assert (tree._bloom_count(), tree._current_phase) == (16, None)

    def test_file_count_resets_between_phases(self):
        tree = BloomingTree(version="0.1.0", target="python", spec_path="x.yaml")

        tree.start_phase("Rendering templates")
        tree.add_file(Path("a.py"))
        tree.add_file(Path("b.py"))
        tree.start_phase("next")

        assert tree._current_files == 0
