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
""" Utilities used to manipulate source code files from student
    assignments. """
import glob
import subprocess
import difflib
import os.path
import logging
import re
import sys
from mkcompiledb import create_clang_compile_commands_db
from logger import setup_logger
from parse_header import dict_header
from header_check import header_check

def remove_cpp_comments(file):
    """ Remove CPP comments from a file using the CPP preprocessor """
    # Inspired by
    # https://stackoverflow.com/questions/13061785/remove-multi-line-comments
    # and
    # https://stackoverflow.com/questions/35700193/how-to-find-a-search-term-in-source-code/35708616#35708616
    no_comments = None
    cmd = 'clang++ -E -P -'
    try:
        with open(file) as file_handle:
            # replace 'a', '__' and '#' to avoid preprocessor handling
            filtered_contents = file_handle.read().replace('a', 'aA').\
            replace('__', 'aB').replace('#', 'aC')
        proc = subprocess.run([cmd], capture_output=True, shell=True, \
            timeout=10, check=False, text=True, input=filtered_contents)
        if proc.returncode == 0:
            no_comments = proc.stdout.replace('aC', '#').replace('aB', '__').replace('aA', 'a')
        else:
            logging.error('Errors encountered removing comments.')
            logging.error('stderr {}'.format(str(proc.stderr).rstrip("\n\r")))
    except FileNotFoundError as exception:
        logging.error('Cannot remove comments. No such file. %s', file)
    return no_comments

def makefile_has_compilecmd(target_makefile):
    """ Given a Makefile, see if it has the compilecmd target which prints
        the compilation command to stdout. """
    has_compilecmd = False

    try:
        with open(target_makefile) as file_handle:
            has_compilecmd = (file_handle.read().find('compilecmd:') != -1)
    except FileNotFoundError as exception:
        logging.error('Cannot open Makefile "%s" for reading.', target_makefile)
    return has_compilecmd

def makefile_get_compilecmd(target_dir, compiler='clang++'):
    """ Given a Makefile with the compilecmd target, return the string
        which represents the compile command. For use with making the
        compile database for linting. """
    compilecmd = None
    makefiles = glob.glob(os.path.join(target_dir, '*Makefile'), recursive=False)
    # Break on the first matched Makefile with compilecmd
    matches = None
    for makefile in makefiles:
        if makefile_has_compilecmd(makefile):
            cmd = 'make -C {} compilecmd'.format(target_dir)
            proc = subprocess.run([cmd], capture_output=True, shell=True, \
                timeout=10, check=False, text=True)
            matches = [line for line in str(proc.stdout).split('\n') if line.startswith(compiler)]
            break
    if matches:
        compilecmd = matches[0]
    else:
        logging.info('Could not identify compile command; using default.')
    return compilecmd

def compare_files(base_file, submission_file):
    """ Compare two source files with a contextual diff, return \
    result as a list of lines. """
    base_file_contents_no_comments = remove_cpp_comments(base_file)
    contents_no_comments = remove_cpp_comments(submission_file)
    diff = ""
    if contents_no_comments and base_file_contents_no_comments:
        base_file_contents_no_comments = base_file_contents_no_comments. \
            split('\n')
        contents_no_comments = contents_no_comments.split('\n')
        diff = difflib.context_diff(base_file_contents_no_comments, \
            contents_no_comments, 'Base', 'Submission', n=3)
    else:
        logging.error('Cannot perform contextual diff.')
    return list(diff)

def format_check(file):
    """ Use clang-format to check file's format against the \
    Google C++ style. """
    # clang-format
    cmd = 'clang-format'
    cmd_options = '-style=Google --Werror'
    cmd = cmd + ' ' + cmd_options + ' ' + file
    proc = subprocess.run([cmd], capture_output=True, shell=True, \
        timeout=10, check=False, text=True)
    correct_format = str(proc.stdout).split('\n')
    with open(file) as file_handle:
        original_format = file_handle.read().split('\n')
    diff = difflib.context_diff(original_format, correct_format, \
        'Student Submission (Yours)', 'Correct Format', n=3)
    #print('\n'.join(list(diff)))
    return list(diff)


def lint_check(file):
    """ Use clang-tidy to lint the file. Options for clang-tidy \
    defined in the function. """
    # clang-tidy
    compilecmd = makefile_get_compilecmd(os.path.dirname(os.path.realpath(file)))
    if compilecmd:
        logging.info('Using compile command %s', compilecmd)
        create_clang_compile_commands_db(remove_existing_db=True, compile_cmd=compilecmd)
    else:
        create_clang_compile_commands_db(remove_existing_db=True)
    cmd = 'clang-tidy'
    cmd_options = r'-checks="-*,google-*, modernize-*, \
    readability-*,cppcoreguidelines-*,\
    -google-build-using-namespace,\
    -google-readability-todo,\
    -modernize-use-trailing-return-type,\
    -cppcoreguidelines-avoid-magic-numbers,\
    -readability-magic-numbers,\
    -cppcoreguidelines-pro-type-union-access,\
    -cppcoreguidelines-pro-bounds-constant-array-index,\
    -cppcoreguidelines-pro-bounds-array-to-pointer-decay"'
    #cmd_options = '-checks="*"'
    cmd = cmd + ' ' + cmd_options + ' ' + file
    proc = subprocess.run([cmd], capture_output=True, shell=True, \
        timeout=10, check=False, text=True)
    linter_warnings = str(proc.stdout).split('\n')
    linter_warnings = [line for line in linter_warnings if line != '']
    return linter_warnings

def glob_cc_src_files(target_dir='.'):
    """ Recurse through the target_dir and find all the .cc files. """
    return glob.glob(os.path.join(target_dir, '*.cc'), recursive=True)

def glob_h_src_files(target_dir='.'):
    """ Recurse through the target_dir and find all the .h files. """
    return glob.glob(os.path.join(target_dir, '*.h'), recursive=True)

def glob_all_src_files(target_dir='.'):
    """ Recurse through the target_dir and find all the .cc and .h files. """
    files = glob_cc_src_files(target_dir) + glob_h_src_files(target_dir)
    return files

def make_spotless(target_dir):
    """ Given a directory that contains a GNU Makefile, clean with the `make
        spotless` target. """
    status = True
    status = make(target_dir, 'spotless')
    return status

def make_build(target_dir, always_clean=True):
    """ Given a directory that contains a GNU Makefile, build with `make all`.
        This function call will call `make spotless` via make_spotless() """
    status = True
    if always_clean:
        status = make_spotless(target_dir)
    if status:
        status = make(target_dir, 'all')
    return status

def make(target_dir, make_target):
    """ Given a directory, execute make_target given the GNU Makefile in the
        directory. """
    status = True
    if not os.path.exists(os.path.join(target_dir, 'Makefile')):
        logging.error('Makefile does not exist in %s', target_dir)
        status = False
    else:
        cmd = 'make -C {} {}'.format(target_dir, make_target)
        logging.debug(cmd)
        proc = subprocess.run([cmd], capture_output=True, shell=True, \
            timeout=15, check=False, text=True)
        #if proc.stdout:
        #    logging.info('stdout: %s', str(proc.stdout).rstrip("\n\r"))
        if proc.stderr:
            logging.info('stderr: %s', str(proc.stderr).rstrip("\n\r"))
        if proc.returncode != 0:
            status = False
    return status

def build(file, target='asgt', compiletimeout=10):
    """ Given a C++ source file, build with clang C++14 with -Wall
        and -pedantic. Output is 'asgt'. Binary is left on the file system. """
    # rm the file if exists
    if os.path.exists(target):
        os.unlink(target)
    status = True
    cmd = 'clang++ -Wall -pedantic -std=c++14 -o {} {}'.format(target, file)
    logging.debug(cmd)
    proc = subprocess.run([cmd], capture_output=True, shell=True, \
        timeout=compiletimeout, check=False, text=True)
    if proc.stdout:
        logging.info('stdout: %s', str(proc.stdout).rstrip("\n\r"))
    if proc.stderr:
        logging.info('stderr: %s', str(proc.stderr).rstrip("\n\r"))
    if proc.returncode != 0:
        status = False
    return status

def identify(header):
    """ String to identify submission's owner. """
    ident = '(Malformed Header)'
    if header:
        ident = 'Grading {} {} {}'.format(header.get('name'),
            header.get('email'), header.get('github'))
    return ident

def has_main_function(file):
    """ Check if a given file has a C++ main function. """
    status = False
    main_regex = re.compile(r'int\s*main\s*\(int\s*argc,\s*(const)?\s*char\s*(const)?\s*\*\s*argv\[\]\)')
    with open(file, 'r') as file_handle:
        src_code = file_handle.read()
        matches = main_regex.search(src_code)
        if matches:
            status = True
    return status

def solution_check_simple(run=None):
    """ Main function for checking student's solution. Provide a pointer to a
        run function. """
    setup_logger()
    if len(sys.argv) < 3:
        logging.error('provide target directory, program name, and optionally a base directory')
        sys.exit(1)
    target_directory = sys.argv[1]
    if len(sys.argv) == 4:
        base_directory = sys.argv[3]
    else:
        base_directory = None
    files = glob_all_src_files(target_directory)
    if len(files) == 0:
        logging.error("No files in %s.", target_directory)
        sys.exit(1)

    # Header checks
    with open(files[0]) as file_handle:
        contents = file_handle.read()
    header = dict_header(contents)
    logging.info('Start %s', identify(header))
    logging.info('All files: %s', ' '.join(files))
    files_missing_header = [file for file in files \
        if not header_check(file)]
    if len(files_missing_header) != 0:
        logging.warning('Files missing headers: %s', ' '.join(files_missing_header))

    # Check if files have changed
    if base_directory:
        count = 0
        for file in files:
            diff = compare_files(file, \
                os.path.join(base_directory, file))
            if len(diff) == 0:
                count += 1
                logging.error('No changes made to the file %s.', file)
        if count == len(files):
            logging.error('No changes made to any files.')
            sys.exit(1)
    else:
        logging.debug('Skipping base file comparison.')

    # Format
    for file in files:
        diff = format_check(file)
        if len(diff) != 0:
            logging.warning('Formatting needs improvement in %s.', file)
            logging.info('Please make sure your code conforms to the Google C++ style.')
            #logging.warning('\n'.join(diff))
        else:
            logging.info('Formatting passed on %s', file)

    # Lint
    for file in files:
        lint_warnings = lint_check(os.path.join(target_directory, file))
        if len(lint_warnings) != 0:
            logging.warning('Linter found improvements in %s.', file)
            #logging.warning('\n'.join(lint_warnings))
        else:
            logging.info('Linting passed in %s', file)

    status = 0
    # Clean, Build, & Run
    cc_files = glob_cc_src_files(target_directory)
    main_src_file = None
    if len(cc_files) > 1:
        logging.warning('Found more than one C++ source file: %s', ' '.join(cc_files))
    for file in files:
        if has_main_function(file):
            main_src_file = file
            break
    if main_src_file:
        logging.info('Checking build for %s', main_src_file)
        if build(main_src_file):
            logging.info('Build passed')
            # Run
            if run('./' + sys.argv[2]):
                logging.info('Run passed')
            else:
                logging.error('Run failed')
                status = 1
        else:
            logging.error('Build failed')
            status = 1
    else:
        logging.error('No main function found in files: %s', ' '.join(cc_files))
        status = 1
    logging.info('End %s', identify(header))
    sys.exit(status)

def solution_check_make(run=None):
    """ Main function for checking student's solution. Provide a pointer to a
        run function. """
    setup_logger()
    if len(sys.argv) < 3:
        logging.error('provide target directory, program name, and optionally a base directory')
        sys.exit(1)
    target_directory = sys.argv[1]
    if len(sys.argv) == 4:
        base_directory = sys.argv[3]
    else:
        base_directory = None
    files = glob_all_src_files(target_directory)
    if len(files) == 0:
        logging.error("No files in %s.", target_directory)
    with open(files[0]) as file_handle:
        contents = file_handle.read()
    header = dict_header(contents)
    logging.info('Start %s', identify(header))
    logging.info('All files: %s', ' '.join(files))
    files_missing_header = [file for file in files \
        if not header_check(file)]
    if len(files_missing_header) != 0:
        logging.warning('Files missing headers: %s', ' '.join(files_missing_header))

    # Check if files have changed
    if base_directory:
        count = 0
        for file in files:
            diff = compare_files(file, \
                os.path.join(base_directory, file))
            if len(diff) == 0:
                count += 1
                logging.error('No changes made in file %s.', file)
        if count == len(files):
            logging.error('No changes made ANY file. Stopping.')
            sys.exit(1)
    else:
        logging.debug('Skipping base file comparison.')

    # Format
    for file in files:
        diff = format_check(file)
        if len(diff) != 0:
            logging.warning("Formatting needs improvement in %s.", file)
            #logging.warning('\n'.join(diff))
        else:
            logging.info('Formatting passed on %s', file)

    # Lint
    #for file in files:
    #    lint_warnings = lint_check(os.path.join(target_directory, file))
    #    if len(lint_warnings) != 0:
    #        logging.warning('Linter found improvements in %s.', file)
    #        #logging.warning('\n'.join(lint_warnings))
    #    else:
    #        logging.info('Linting passed in %s', file)

    status = 0
    # Clean, Build, & Run
    if make_build(target_directory):
        logging.info('Build passed')
        # Run
        if run(os.path.join(target_directory, sys.argv[2])):
            logging.info('Run passed')
        else:
            logging.error('Run failed')
            status = 1
    else:
        logging.error('Build failed')
        status = 1
    logging.info('End %s', identify(header))
    sys.exit(status)
