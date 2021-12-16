#!/usr/bin/env python3
import sys
import os
import subprocess
import logging

# Read history from argv[1], output filtered input to argv[2], and log to
# argv[3]. If any lines cannot be decoded as utf-8, they will be kept.

INPUT_FILENAME = sys.argv[1]
OUTPUT_FILENAME = sys.argv[2]
LOG_FILENAME = sys.argv[3]

# see https://www.zsh.org/mla/users/2011/msg00154.html
UNMETAFY = os.path.join(sys.path[0], 'unmetafy')

logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')


def handle_decode(byte_line: bytes, outfileobj):
    try:
        decoded = byte_line.decode('utf-8')
    except UnicodeDecodeError:
        # see https://www.zsh.org/mla/users/2011/msg00154.html
        try:
            with subprocess.Popen([UNMETAFY],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE) as proc:
                try:
                    unmetafied = proc.communicate(byte_line, timeout=1)[0]
                except subprocess.TimeoutExpired:
                    proc.kill()
                    logging.error(
                        'OUTPUT=%s unmetafy timeout error; keeping '
                        'line %s', OUTPUT_FILENAME, byte_line)
                    outfileobj.write(byte_line)
                    return None
        except FileNotFoundError:
            logging.error(
                'OUTPUT=%s unmetafy (%s) not found; '
                'keeping line %s', OUTPUT_FILENAME, UNMETAFY, byte_line)
            outfileobj.write(byte_line)
            return None
        try:
            decoded = unmetafied.decode('utf-8')
        except UnicodeDecodeError:
            logging.warning(
                'OUTPUT=%s UnicodeDecodeError retains; '
                'keeping line %s', OUTPUT_FILENAME, byte_line)
            outfileobj.write(byte_line)
            return None
    return decoded


occurred = set()
skipped_count = 0
try:
    with open(INPUT_FILENAME, 'rb') as infile, \
         open(OUTPUT_FILENAME, 'wb') as outfile:
        for bline in infile:
            line = handle_decode(bline, outfile)
            if line is None:
                continue

            line = line.strip()

            # at least two words in line,
            # and at least 15 characters long;
            # command too simple needn't history
            if len(line.split(maxsplit=1)) <= 1:
                skipped_count += 1
                continue
            if len(line) < 15:
                skipped_count += 1
                continue

            # at most 80 characters in line;
            # command too long is hard to reuse
            if len(line) > 80:
                skipped_count += 1
                continue

            # does not start with '#' character
            if line.startswith('#'):
                skipped_count += 1
                continue

            # remove duplicate lines
            if line in occurred:
                skipped_count += 1
                continue

            outfile.write(bline.strip())
            outfile.write(b'\n')
            occurred.add(line)
    if skipped_count:
        logging.info('OUTPUT=%s filtered out %d lines', OUTPUT_FILENAME,
                     skipped_count)
finally:
    logging.shutdown()
