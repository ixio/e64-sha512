#!/usr/bin/env python3

"""A strong password generator"""

import argparse
import getpass
import pbkdf2
try:
    import clipboard
except ImportError:
    print("WARNING: For clipboard management run pip install clipboard")

ARGS = argparse.ArgumentParser(description="Output a strong password")
ARGS.add_argument("name",type=str)
ARGS.add_argument("-n",type=int,default=12)
ARGS.add_argument("-i",type=int,default=10000)

SALT = b"998c5ef69cf2a36f2a0f9dfcac1a878a"

class Chars:
    """Iterator that yields wanted characters"""
    def __init__(self):
        self.bounds = [(35,37),42,(48,58),(64,72),(74,78),80,(82,90),(97,107),(109,122)]

    def __iter__(self):
        return self

    def __next__(self):
        if self.bounds:
            h, *t = self.bounds
            if type(h) == int:
                self.bounds = t
                return chr(h)
            a, b = h
            if a == b:
                self.bounds = t
            else:
                self.bounds = [(a+1,b)]+t 
            return chr(a)
        raise StopIteration

    def chars(self):
        """Returns a list of the characters contained in Chars"""
        chars = []
        for c in Chars():
            chars.append(c)
        return chars

def trad(s):
    """Translates a unicode string in a string of Char characters"""
    chars = Chars().chars()

    def trad_num(n):
        (d, m) = divmod(n,len(chars))
        if d > 0:
            return trad_num(d) + chars[m]
        return chars[m]
    
    return trad_num(int("".join([str(c) for c in s])))

def is_secure(s):
    """Returns if a string is secure i.e. contains all the differents types of Chars"""
    types = [0,0,0,0]
    for c in s:
        if ord(c) >= 48 and ord(c) <= 58:
            types[0] += 1
        elif ord(c) >= 65 and ord(c) <= 90:
            types[1] += 1
        elif ord(c) >= 97 and ord(c) <= 122:
            types[2] += 1
        else:
            types[3] += 1
    res = True
    for counter in types:
        res &= counter > 0
    return res

def encode(to_encode, iterations, size = 64):
    """Returns a translated PBKDF2 hash from string input and SALT"""

    pbkdf2_hash = pbkdf2.PBKDF2(to_encode,SALT,iterations).read(size)
    return trad(pbkdf2_hash)

def main():
    """Main program.

    Parse arguments, prepare sha512, get master password, return secure password.
    """
    args = ARGS.parse_args()

    master_passwd = getpass.getpass(prompt="Master password:")

    seed = args.name + master_passwd
    passwd = encode(seed,args.i)[:args.n]

    while not is_secure(passwd):
        to_encode += "*"
        passwd = encode(seed,args.i)[:args.n]

    try:
        clipboard.copy(passwd)
    except NameError:
        pass

    return passwd

if __name__ == '__main__':
    print(main())
