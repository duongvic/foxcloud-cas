import string
import random

LETTERS = string.ascii_letters


def gen_key(size=10, chars=LETTERS + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def join_args(sep, *args):
    """

    @param sep:
    @type sep:
    @param args:
    @type args:
    @return:
    @rtype:
    """
    return sep.join(args)


def h_join(*args):
    """

    @param args:
    @type args:
    @return:
    @rtype:
    """
    return '-'.join(args)

