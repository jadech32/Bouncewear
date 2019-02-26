from classes.converse import Converse
import os

if __name__ == '__main__':
    os.environ['PYTHONWARNINGS'] = "ignore:Unverified HTTPS request"
    c = Converse(["westbrook"])
    c.webhook()
    c.run()

