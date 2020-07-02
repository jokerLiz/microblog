import unittest



class TestClass(unittest.TestCase):
    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_add(self):
        print('test_add')
        x = 33
        y = 90
        self.assertEqual(x+y,123)

    def test_list(self):
        print('test_list')
        list = [1,2,3]
        self.assertTrue(len(list)==3)
