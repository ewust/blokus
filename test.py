import unittest

if __name__ == "__main__":
    for module in unittest.defaultTestLoader.discover(".", pattern="*_test.py"):
        unittest.TextTestRunner(verbosity=2).run(module)
    