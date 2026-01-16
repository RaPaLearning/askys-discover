import unittest
import os
import json
import sys
import random
from urllib.parse import quote

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'askys-discover'))
from main import app, search


class TestSearchResults(unittest.TestCase):
    def assert_all_search_results(self, search_results: str, expected_filenames: list[str]):
        self.assertEqual(len(search_results), len(expected_filenames))
        filenames = [result.filename for result in search_results]
        self.assertTrue(all(expected_file in filenames for expected_file in expected_filenames),)

    def assert_search_includes(self, search_results: str, expected_filenames: list[str]):
        filenames = [result.filename for result in search_results]
        self.assertTrue(all(expected_file in filenames for expected_file in expected_filenames),
                        f"Expected filenames {expected_filenames} not all found in search results {filenames}")

    def test_search_one_word(self):
        search_results = search("karma")
        self.assertIsInstance(search_results, list)
        for result in search_results:
            self.assertIn("karma", result.content.lower())
            self.assertFalse(result.content.startswith('## '))  # Ensure whole text not returned
    
    def test_search_phrase(self):
        self.assertEqual(search("origin of Brahma")[0].filename, '11-37_part_1.md')
        self.assertEqual(search("origin of  Brahma")[0].filename, '11-37_part_1.md')
        self.assertEqual(search("Origin of Brahma")[0].filename, '11-37_part_1.md')
    
    def test_search_phrase_with_typos(self):
        self.assertEqual(search("origin of Bramha")[0].filename, '11-37_part_1.md')

    def test_search_phrase_with_hyperlink(self):
        self.assertEqual(search("expand My devotion")[0].filename, '10-1.md')

    def test_devanagari_word(self):
        self.assertEqual(search("भूतभृत्")[0].filename, '9-4_to_9-5.md')
    
    def test_devanagari_phrase(self):
        self.assert_search_includes(search("योगम् ऐश्वरम्"), ['9-4_to_9-5.md', '11-8.md'])

    def test_devanagari_sandhi(self):
        self.assert_search_includes(search("योगमैश्वरम्"), ['9-4_to_9-5.md', '11-8.md'])

    def test_vocabulary_match(self):
        self.assert_search_includes(search('good begets good'), ['5-11.md'])

    def test_semantic_match(self):
        self.assert_search_includes(search('insignificant in comparison to a mountain'), ['6-47.md'])

    def test_semantic_match_in_meaning(self):
        meaning_search_results = search('just as you would perform with attachment, work without attachment')
        self.assert_search_includes(meaning_search_results, ['3-25_to_3-26.md'])

def get_request(test_client, url: str):
    return test_client.get(url,
        headers={'Authorization': f'Bearer {''.join([str(random.randint(0, 9)) for _ in range(31)])}'})

class TestGitaSearchRoute(unittest.TestCase):
    """Test the /gita/ route."""
    
    def setUp(self):
        # app is an instance of Flask imported from main.py
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_gita_search_with_query(self):
        """Test /gita/ route with a valid query parameter."""
        response = get_request(self.client, '/gita/?q=karma')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.get_data(as_text=True))
        
        self.assertEqual(data['to_search'], 'karma')
        self.assertIn('version', data)
        self.assertGreater(len(data['matches']), 0)
            
    def test_gita_search_without_query(self):
        """Test /gita/ route without query parameter."""
        response = get_request(self.client, '/gita/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.get_data(as_text=True))
        
        self.assertIsNone(data['to_search'])
        self.assertIn('version', data)
        self.assertEqual(data['errors'], 'No search query provided.')
        self.assertNotIn('matches', data)
    
    def test_gita_search_with_empty_query(self):
        """Test /gita/ route with empty query parameter."""
        response = get_request(self.client, '/gita/?q=')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        
        # Empty string is falsy, so it should trigger the error case
        self.assertEqual(data['to_search'], '')
        self.assertEqual(data['errors'], 'No search query provided.')
    
    def test_gita_search_with_special_characters(self):
        """Test /gita/ route with special characters in query."""
        special_query = "test@#$%^&*()"
        response = get_request(self.client, f'/gita/?q={quote(special_query)}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        
        self.assertEqual(data['to_search'], special_query)
    
    def test_gita_search_with_unicode_query(self):
        """Test /gita/ route with unicode characters."""
        unicode_query = "धर्म"
        response = get_request(self.client, f'/gita/?q={unicode_query}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        
        self.assertEqual(data['to_search'], unicode_query)
        self.assertGreater(len(data['matches']), 0)
        for result in data['matches']:
            self.assertIn("धर्म", result['match_text'])

    
    def test_gita_search_version_from_environment(self):
        """Test that version is correctly read from environment variable."""
        response = get_request(self.client, '/gita/?q=test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertGreater(len(data['version']), 0)
    

class TestFlaskApp(unittest.TestCase):
    """Test Flask app configuration and general functionality."""
    
    def setUp(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_app_exists(self):
        """Test that the Flask app instance exists."""
        self.assertIsNotNone(app)
        self.assertIsInstance(app, app.__class__)
    
    def test_invalid_route(self):
        """Test accessing a non-existent route."""
        response = get_request(self.client, '/nonexistent/')
        self.assertEqual(response.status_code, 404)
    
    def test_gita_route_methods(self):
        """Test that /gita/ route only accepts GET requests."""
        # GET should work
        response = get_request(self.client, '/gita/?q=test')
        self.assertEqual(response.status_code, 200)
        
        # POST should return 405 Method Not Allowed
        response = self.client.post('/gita/', data={'q': 'test'})
        self.assertEqual(response.status_code, 405)
        
        # PUT should return 405 Method Not Allowed
        response = self.client.put('/gita/', data={'q': 'test'})
        self.assertEqual(response.status_code, 405)

    def test_search_result_data_structure(self):
        response = get_request(self.client, '/gita/?q=test')
        data = json.loads(response.get_data(as_text=True))
        
        for match in data['matches']:
            # Verify required fields exist
            self.assertIn('filename_no_mdext', match)
            self.assertIn('match_id', match)
            self.assertIn('match_score', match)
            self.assertIn('match_text', match)
            
            # Verify data types
            self.assertIsInstance(match['filename_no_mdext'], str)
            self.assertIsInstance(match['match_id'], int)
            self.assertIsInstance(match['match_score'], (int, float))
            self.assertIsInstance(match['match_text'], str)
            
            # Verify score is between 0 and 1
            self.assertGreater(match['match_score'], 0)
    
    def test_search_result_content(self):
        """Test specific mock data content."""
        response = get_request(self.client, '/gita/?q=dharma')
        data = json.loads(response.get_data(as_text=True))
        
        matches = data['matches']
        self.assertGreater(len(matches), 0)
        
        self.assertRegex(matches[0]['filename_no_mdext'], r'\d+-\d+')
        self.assertIsNotNone(matches[0]['match_score'])
        self.assertIn('dharma', matches[0]['match_text'])


if __name__ == '__main__':
    unittest.main()
    