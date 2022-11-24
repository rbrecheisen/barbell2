import sys
import argparse


def setup_args_env(arg_list):
    for arg in arg_list:
        sys.argv.append(arg)


def get_parser():
    return argparse.ArgumentParser()
