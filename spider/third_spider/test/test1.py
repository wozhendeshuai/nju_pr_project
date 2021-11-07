import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        num=1;
        file = open('F:\\access_token.txt', 'r')
        list = file.readlines()
        lines = len(list)
        # str = file.readline()
        print(lines)
        str = list[num % 2]
        file.close()
        print(str)



if __name__ == '__main__':
    unittest.main()
