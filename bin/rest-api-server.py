#!/usr/bin/env python2
from iCE import rest_api


def main():
    api = rest_api.APIServer()
    api.run()

if __name__ == '__main__':
    main()
