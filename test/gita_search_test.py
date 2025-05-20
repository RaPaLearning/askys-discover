from qdrant_client import QdrantClient
import unittest
import shutil
import os
import importlib.util


def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGitaSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.embedder = module_from_file('gita_begin_embed', os.path.join(os.path.dirname(__file__), '..', 'askys-create-embed', 'gita_begin_embed.py'))
        test_folder = os.path.join(os.path.dirname(__file__), '..', 'test')
        vdb_path = os.path.join(test_folder, cls.embedder.VDB_DIRNAME)
        if os.path.exists(vdb_path) and os.path.isdir(vdb_path):
            shutil.rmtree(vdb_path)
        paras, filenames = cls.embedder.get_paragraphs_from_md(os.path.join('test', 'gita-begin-samples'))
        cls.embedder.to_qdrant(paras, filenames, vdb_path)
        cls.vdb_path = vdb_path
        cls.client = QdrantClient(path=vdb_path)

    def assert_query_result(self, query_text, expected_source, expected_phrase=None):
        search_result = self.client.query(
            collection_name=self.embedder.VDB_COLLECTION_NAME,
            query_text=query_text,
            limit=3,
        )
        self.assertEqual(search_result[0].metadata['source'], expected_source)
        if expected_phrase: self.assertIn(expected_phrase, search_result[0].document)

    def test_english_query_phrase_gives_closest_match(self):
        self.assert_query_result("self purification", "5-11.md", "purify the Self")
        self.assert_query_result("can't know the Lord", "10-2.md", "cannot be recognized")
        self.assert_query_result("seeing commonality in variety is in sattva", "18-20.md", "not subject to any of this variety")

    def test_transliteration_query_word_gives_exact_match(self):
        self.assert_query_result("karma", "5-11.md", "karma")
        self.assert_query_result("prabhavam", "10-2.md", "prabhavam")
        self.assert_query_result("bhAvam", "18-20.md", "bhAvam")

    def test_phrase_in_link_gives_exact_match(self):
        self.assert_query_result("karmayOga", "5-11.md")
        self.assert_query_result("gods", "10-2.md", "gods")

    def sanskrit_query_word_gives_exact_match(self):
        self.assert_query_result("कर्म", "5-11.md", "कर्म")
        self.assert_query_result("प्रभवम्", "10-2.md", "प्रभवम्")
        self.assert_query_result("भावम्", "18-20.md", "भावम्")


if __name__ == '__main__':
    unittest.main()
