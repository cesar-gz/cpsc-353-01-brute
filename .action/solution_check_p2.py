#!/usr/bin/env python3
#
# Copyright 2021 Michael Shafae
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
""" Check student's submission; requires the main file and the
    template file from the original repository. """
# pexpect documentation
#  https://pexpect.readthedocs.io/en/stable/index.html
import io
import logging
#import pexpect
from srcutilities import solution_check_make
import subprocess
from hashlib import md5
from PIL import Image
import os.path

# to run locally 
# PYTHONPATH=../.action python3 ../.action/solution_check_p1.py . mind_reader

def run(binary):
    """ Run part-1 """
    status = True
    values = (
        ('imagetest.png',),
           )
    for index, val in enumerate(values):
        logging.info('Test %d - %s', index + 1, val)
        _status = _run(binary, val)
        status = status and _status
        #if not status:
        #    logging.error("Did not receive expected response. Halting test.")
        #    break
    return status


def _run(binary, values):
    """ This is the test for the BMR program given the inputs from run_p1 """
    status = False
    #values = list(map(str, values))
    cmd = "{} {}".format(binary, values[0])

    # 512 x 512 image
    md5sum = 'ff9d84c964fe78810b2114d406d3f522'

    logging.info('Executing "%s"', cmd)
    proc = subprocess.run([cmd], capture_output=True, shell=True, \
        timeout=1, check=False, text=True)
    if proc.returncode == 0:
        cksum = md5()
        with Image.open(values[0]) as img:
            if img.size == (512, 512):
                with open(values[0], 'rb') as fh:
                    cksum.update(fh.read())
                    status = (cksum.hexdigest() == md5sum)
                    if not status:
                        logging.error('Image does not pass checksum test.')
            else:
                logging.error('Image size is not 512 x 512 pixels.')
                status = False

    else:
        logging.error('Errors encountered.')
        logging.error('stderr {}'.format(str(proc.stderr).rstrip("\n\r")))

    if os.path.exists(values[0]):
        os.unlink(values[0])

    return status


if __name__ == '__main__':
    print('There is not a system test for this part.')
    #solution_check_make(run=run)
