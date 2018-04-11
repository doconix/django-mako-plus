#!/usr/bin/env python3
'''
Created by Conan Albrecht <doconix@gmail.com>
Apache open source license.
November, 2017
'''
##################################################
###  Unique id generator.  Similar to uuid1() but 
###  also includes the process id.
###
###  Note that upping the counter requires a global lock.
###
###  The bit assignment:
###  
###      52 bits for nanoseconds since epoch (really it can use unlimited bits because on left side of the number, but 52 bits gets us to ~2100)
###      16 bits for counter
###      48 bits for machine id
###      24 bits for process id
###   ========
###     140 bits total, or 35 hex characters 
###  
###  Maximum number is 1.39e42
###

import uuid
import time as time  
import os
import random
import threading
import math
import collections
    
    
# initial values/constants
lastnow = 0
counterstart = random.getrandbits(16) - 1
countermax = math.pow(2, 16) - 1
counter = counterstart
# returns a 48 bit number
machineid = uuid.getnode()
# linux is usually 16 bits
processid = os.getpid()

# the main data structure
UID = collections.namedtuple('UID', ( 'time', 'counter', 'machine', 'process' ))

# binary size of each number
# and binary positions for shifting
# and for splitting hex and binary (from right side)
size = UID(52, 16, 48, 24)
_shift = []
for i in reversed(range(len(size))):
    _shift.append(sum(size[i:]))
shift = UID(*reversed(_shift))
hsplit = UID(*(int(s/-4) for s in shift))
bsplit = UID(*(s*-1 for s in shift))

######################################
###  Main API

def ruid():
    '''
    Creates a "raw" unique id.  The result is a
    UID namedtuple with four parts:
    
        time
        counter
        machine
        process
    
    All other functions in this module just format
    the id created in this function.
    '''
    global lastnow, counter_start, counter
    # update the nanoseconds and counter
    with threading.RLock():
        now = int(time.time())#int(time.time() * 1e6)
        counter += 1
        if counter >= countermax:
            counter = 0
        while now == lastnow and counter == counterstart:
            time.sleep(.001)  # wait a millisecond and try again
            now = int(time.time())#int(time.time() * 1e6)
        lastnow = now
    # return the named tuple
    return UID(now, counter, machineid, processid)
    

def iuid(raw=None):
    '''
    Creates a unique id as an int. 

    If provided, raw should be a UID named tuple
    (usually from a call to ruid).
    '''    
    if raw is None:
        raw = ruid()
    return (raw.time << shift.counter) + \
           (raw.counter << shift.machine) + \
           (raw.machine << shift.process) + \
           (raw.process)
    

def uid(raw=None, sep=None):
    '''
    Creates a unique id as a hex string. 

    If provided, raw should be a UID named tuple
    (usually from a call to ruid).
    
    Use sep='-' to separate the parts by dashes.
    '''
    if raw is None:
        raw = ruid()
    # hex version
    if sep is None:
        return '{:0x}'.format(iuid(raw))
    # pretty version
    n = uid(raw)
    return sep.join((
        n[:hsplit.counter], 
        n[hsplit.counter: hsplit.machine], 
        n[hsplit.machine: hsplit.process], 
        n[hsplit.process:],
    ))
    
    
def buid(raw=None, sep=None):
    '''
    Creates a unique id as a binary string. 

    If provided, raw should be a UID named tuple
    (usually from a call to ruid).
    
    Use sep='-' to separate the parts by dashes.
    '''
    if raw is None:
        raw = ruid()
    # hex version
    if sep is None:
        return '{:0b}'.format(iuid(raw))
    # pretty version
    n = buid(raw)
    return sep.join((
        n[:bsplit.counter], 
        n[bsplit.counter: bsplit.machine], 
        n[bsplit.machine: bsplit.process], 
        n[bsplit.process:],
    ))
    

def wuid(raw=None, leading='u'):
    '''
    Creates a unique id as a web-compliant id
    for use in HTML ids.  This is the same as 
    a hex id, but it has a leading `u` to ensure
    an alphabetical character comes first, per 
    the standard.

    If provided, raw should be a UID named tuple
    (usually from a call to ruid).

    Use sep='-' to separate the parts by dashes.
    '''
    if raw is None:
        raw = ruid()
    return '{}{}'.format(leading, uid(raw))
    

def iunpack(n):
    '''
    Unpacks the given integer number
    into a UID namedtuple.
    '''
    # format of these is (mask & n) >> shifted
    return UID(
        n >> shift.counter,
        ((((1 << size.counter) - 1) << shift.machine) & n) >> shift.machine,
        ((((1 << size.machine) - 1) << shift.process) & n) >> shift.process,
          ((1 << shift.process) - 1) & n,
    )
    
 
def unpack(hex_n):
    '''
    Unpacks the given hex number string
    into a UID namedtuple.
    
    To unpack a web id, use
        unpack(myid[1:])
    to remove the leading character.
    '''
    return iunpack(int(hex_n, 16))
    
    
    
    
###################################################
###  Unit tests for this module:
###
###     python3 uid.py
###

import unittest

class Tester(unittest.TestCase):

    def test_ruid(self):
        u = ruid()
        u2 = ruid()
        self.assertEqual(u.machine, u2.machine)
        self.assertEqual(u.process, u2.process)

    def test_int_hex_binary(self):
        u = ruid()
        n = iuid(u)
        h = uid(u)
        b = buid(u)
        self.assertEqual(n, int(h, 16))
        self.assertEqual(n, int(b, 2))
        
    def test_int_hex_binary(self):
        u = ruid()
        n = iuid(u)
        h = uid(u)
        b = buid(u)
        self.assertEqual(n, int(h, 16))
        self.assertEqual(n, int(b, 2))
        
    def test_pretty(self):
        u = ruid()
        # hex
        h = uid(u)
        p = uid(u, '-')
        self.assertEqual(h, p.replace('-', ''))
        # binary
        b = buid(u)
        p = buid(u, '-')
        self.assertEqual(b, p.replace('-', ''))

    def test_unpack(self):
        # one test
        u = ruid()
        self.assertEqual(u, unpack(uid(u)))
        self.assertEqual(u, iunpack(iuid(u)))
        # other direction with int
        n = iuid()
        self.assertEqual(n, iuid(iunpack(n)))
        # other direction with hex
        h = uid()
        self.assertEqual(h, uid(unpack(h)))
        
if __name__ == '__main__':
    unittest.main()
        