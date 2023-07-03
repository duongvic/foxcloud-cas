#
# Copyright (c) 2020 FTI-CAS
#

import hashlib
import pathlib
import os

import paramiko
from cryptography.hazmat.primitives import serialization


def hash_as_hex(value, method='md5'):
    """
    Calculate hash for the value in HEX.
    :param value:
    :param method:
    :return:
    """
    hasher = getattr(hashlib, method)()
    hasher.update(value)
    return hasher.hexdigest()


def gen_ssh_key_(key_filename, bit_count=2048):
    """
    docstring?
    :param key_filename:
    :param bit_count:
    :return:
    """
    key_dir = "{}/.ssh/".format(str(pathlib.Path.home()))
    key_path = key_dir + key_filename
    if not os.path.exists(key_dir):
        os.makedirs(key_dir)
    rsa_key = paramiko.RSAKey.generate(bits=bit_count)
    public_key = str(rsa_key.get_name() + ' ' + rsa_key.get_base64() + '\n')

    os.system("ssh-add  " + key_path)
    with open('.'.join([key_path, "pub"]), "w") as pubkey_file:
        pubkey_file.write(public_key)

    with open(key_path, 'r') as content_file:
        private_key = content_file.read()

    return key_path, private_key, public_key


def gen_ssh_key(bit_count=2048):
    """
    Gen SSH ras_key pair.
    :param bit_count:
    :return:
    """
    ras_key = paramiko.RSAKey.generate(bits=bit_count)
    public_key = ras_key.get_name() + ' ' + ras_key.get_base64() + '\n'
    private_key = ras_key.key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode()
    return private_key, public_key
