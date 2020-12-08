"""
    RDT implementation.

    @author: Wenxuan SHI, and others.
"""


from udp import UDPsocket
import argparse


def main(*, method):
    if method == 'GBN':
        pass
    elif method == 'SR':
        pass
    else:
        raise "Unsupported Method."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', type=str, default='GBN',
                        choices=['GBN', 'SR'])
    main(**(vars(parser.parse_args())))
