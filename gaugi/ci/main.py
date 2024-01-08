#
#   Call ALL your CI scripts from here
#

from test_import import test_import

if __name__ == '__main__':
    print (" ===> BEGIN CI TEST <=== ")
    print (" ==> Import Gaugi test")
    test_import()