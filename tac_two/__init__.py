import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tac_two")


# this is the initial module of your app
# this is executed whenever some client-code is calling `import tac_two` or `from tac_two import ...`
# put your main classes here, eg:
class MyClass:
    def my_method(self):
        return "Hello World"


def main():
    # this is the main module of your app
    # it is only required if your project must be runnable
    # this is the script to be executed whenever some users writes `python -m tac_two` on the command line, eg.
    x = MyClass().my_method()
    print(x)


# let this be the last line of this file
logger.info("tac_two loaded")
