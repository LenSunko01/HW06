import os
from parser import *

PATH = 'tests'

tests = os.listdir(PATH)


def test():
    passed = 0
    testsnum = 0
    for file in tests:
        testsnum += 1
        File = PATH + '/' + file
        with open(File, "r") as f:
            data = f.read()
        try:
            res = Parser.program.parse(data)
        except:
            print("Filename: " + str(file))
            print("Unable to parse")
            continue
        if file[0] == 'a':
            print("Filename: " + str(file))
            print(data)
            assert type(Parser.program.parse(data)) == Success
            print(str(Parser.program.parse(data).value))
            print("\n\n ------------------------------------------------ \n\n")
            passed += 1
        elif file[0] == 'r':
            assert type(Parser.program.parse(data)) == Failure
            passed += 1

    print("%d/%d tests passed" % (passed, testsnum))


if __name__ == "__main__":
    test()
