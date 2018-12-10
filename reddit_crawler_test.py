import unittest
from reddit_crawler import crawl_reddit


class CrawlRedditTest(unittest.TestCase):
    
    def test_values(self):
        '''Make sure value errors are raised when needed'''
        self.assertRaises(ValueError, crawl_reddit, "", 40)
        self.assertRaises(ValueError, crawl_reddit, "Neil", 5)
        
    def test_types(self):
        '''Make sure type error are caught and raised'''
        self.assertRaises(TypeError, crawl_reddit, 'deGrasse', 'Tyson')
        self.assertRaises(TypeError, crawl_reddit, 10, 40)
        
    def test_equals(self):
        '''Test if results are equal'''
        self.assertEqual(self, crawl_reddit(sample_input(), 40), sample_output())