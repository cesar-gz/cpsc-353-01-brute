![Build](../../actions/workflows/build.yml/badge.svg)
![Format](../../actions/workflows/format.yml/badge.svg)
![Header](../../actions/workflows/header.yml/badge.svg)
![Lint](../../actions/workflows/lint.yml/badge.svg)

# CPSC 353 - Assignment 01

This is an academic exercise in cracking passwords for some imaginary people. Whether you want to be an evil doer or a vigilant saint, you can pick the fictional universe along with your motives to suit your fantasies. 

You have some how obtained a password file from a computer. (A copy of the file named `master.passwd` is in your repository.) The passwords have been hashed using DES. You want to decrypt the passwords for motives only known to you. Using C++, write a program to decrypt the passwords!

Completing this exercise ought to make you feel like an [3l173 h4ck3r](https://en.wikipedia.org/wiki/Leet) however let's be real. The approach you take to decrypt the passwords may work - just not within this assignment's deadline. That's OK. This is an academic exercise to gain an appreciation for how this stuff works. (And there are at least two passwords in the list that are easy to decrypt.)

You know that the passwords are encrypted using `crypt()` which means that it is using the DES hashing algorithm and that 12 bits of random salt is encoded as the first two characters of the encrypted password. Furthermore, you know that the unencrypted passwords are at least 1 character in length (not zero) and at most 8 characters in length which results in an 11 character DES hash. In total, the encrypted password is 13 characters in length, 11 for the encrypted password and 2 for the salt.

You know that the passwords are created using visible ASCII characters and that _most_ of the passwords in the list use only the letters A-Z and a-z. Some of the passwords include the numbers 0-9 and extended characters (' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', and '~').

There are many strategies you can use to decrypt the passwords.

The first strategy to consider is using a dictionary of words. Dictionaries in many different languages are available for Linux. On Ubuntu 20.04 the following dictionaries are available:

* wamerican/focal 2018.04.16-1 all
  American English dictionary words for /usr/share/dict

* wamerican-huge/focal 2018.04.16-1 all
  American English dictionary words for /usr/share/dict

* wamerican-insane/focal,now 2018.04.16-1 all [installed]
  American English dictionary words for /usr/share/dict

* wamerican-large/focal 2018.04.16-1 all
  American English dictionary words for /usr/share/dict

* wamerican-small/focal 2018.04.16-1 all
  American English dictionary words for /usr/share/dict

* wbrazilian/focal 3.0~beta4-22 all
  Brazilian Portuguese wordlist

* wbritish/focal 2018.04.16-1 all
  British English dictionary words for /usr/share/dict

* wbritish-huge/focal 2018.04.16-1 all
  British English dictionary words for /usr/share/dict

* wbritish-insane/focal 2018.04.16-1 all
  British English dictionary words for /usr/share/dict

* wbritish-large/focal 2018.04.16-1 all
  British English dictionary words for /usr/share/dict

* wbritish-small/focal 2018.04.16-1 all
  British English dictionary words for /usr/share/dict

* wbulgarian/focal 4.1-7 all
  Bulgarian dictionary words for /usr/share/dict

* wcanadian/focal 2018.04.16-1 all
  Canadian English dictionary words for /usr/share/dict

* wcanadian-huge/focal 2018.04.16-1 all
  Canadian English dictionary words for /usr/share/dict

* wcanadian-insane/focal 2018.04.16-1 all
  Canadian English dictionary words for /usr/share/dict

* wcanadian-large/focal 2018.04.16-1 all
  Canadian English dictionary words for /usr/share/dict

* wcanadian-small/focal 2018.04.16-1 all
  Canadian English dictionary words for /usr/share/dict

* wcatalan/focal 0.20111230b-12 all
  Catalan dictionary words for /usr/share/dict

* wesperanto/focal 2.1.2000.02.25-57 all
  Esperanto dictionary words for /usr/share/dict

* wfrench/focal 1.2.5-1 all
  French dictionary words for /usr/share/dict

* wgaelic/focal 0.50-13 all
  Scots Gaelic word list

* wgerman-medical/focal 20160103-3 all
  German medical dictionary words for /usr/share/dict

* wirish/focal 2.0-27 all
  Irish (Gaeilge) dictionary words for /usr/share/dict

* witalian/focal 1.10 all
  Italian dictionary words for /usr/share/dict/

* wmanx/focal 0.50-16 all
  Manx Gaelic dictionary words for /usr/share/dict

* wpolish/focal 20190812-1 all
  Polish dictionary words for /usr/share/dict

* wportuguese/focal 20190329-3 all
  European Portuguese wordlist

* wspanish/focal 1.0.28 all
  Spanish dictionary words for /usr/share/dict

* wswedish/focal 1.4.5-2.2 all
  Swedish dictionary words for /usr/share/dict

* wukrainian/focal 1.7.1-2 all
  Ukrainian dictionary words for /usr/share/dict

Installing any of the above dictionaries can be done with `apt`. The following command will install the insanely large American English dictionary into the directory `/usr/share/dict/`. You can install as many dictionaries you like.

```
sudo apt install wamerican-insane
```

The dictionaries contain one word per line. It is trivial to read the file line by line and hash each word given the salts contained in `master.passwd`.

Following this strategy, you may attempt to transform letters in a given word. For example, replace all the 'o' letters with '0' numerals, replacing 'i' letters with '1' numerals, or manipulating the capitalization of the word.

Another strategy is to exhaustively search through the space of all possible passwords. This brute force approach is time intensive since an 8 character password selected from a space of 96 characters means that there are 7,213,895,789,838,336 (7 quadrillion!!) possible passwords. With 12 bits of salt, the space goes from 7 quadrillion to 29,548,117,155,177,824,256 (29 quintillion!!!) possible hashes. Thankfully, the salt is given with every password hash so you only have to each through 7 quadrillion choices.

Using a naïve benchmark on an Intel Core i5 6500 processor (3.2 GHz), approximately 275,000 hashes were calculated per second. This means that searching through all 7 quadrillion possible passwords will take about 831 years on the benchmarked system.

Another strategy is to use [cryptanalysis](https://en.wikipedia.org/wiki/Cryptanalysis) to break the encryption. Unfortunately, that strategy is explored further in [a different class](http://catalog.fullerton.edu/preview_course_nopop.php?catoid=70&coid=495362&).

One could attempt to speed up the search by using [multiple processes](http://manpages.ubuntu.com/manpages/focal/en/man3/fork.3posix.html), [threads](https://en.cppreference.com/w/cpp/thread), [distribute the workload to many computers](https://www.open-mpi.org/), or use an [FP](https://iacr.org/workshops/ches/ches2002/presentations/Bond.pdf)[GA](http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=96694D7A7D4EB9774E88228B85C73EA9?doi=10.1.1.19.6350&rep=rep1&type=pdf) or GPU as a coprocessor.

# Unix Password Files

The traditional way passwords were stored on Unix system is to store the passwords as cryptographic hashes in a file named `master.passwd` or `shadow`. On Ubuntu systems, the hashed passwords are stored in `/etc/shadow` which is only readable to the root user.

An example entry is given below with many of the fields filled in. It is common to have fields left empty.

```
mshafae:rG.J5YiPT5Mok:6610:6610:des_users:0:0:Michael Shafae:/home/mshafae:/bin/csh
```

Each field is separated by a ':'. The names of the field are:

* Name
* Encrypted password
* User ID
* Group ID
* Class
* Password change date
* Password expire date
* Gecos (name)
* Home directory
* Shell

For this exercise, our attention is only on encrypted password.

# Requirements

Write a program that takes at least one argument from the command line. The first argument is a file that contains the passwords written in the traditional Unix password file format. 

Using whatever strategies you like, with code that you have written yourself, decrypt the passwords.

Report your results by inputting the passwords you cracked into the Password Cracking Quiz on Canvas. This will give you immediate feedback if your answer is correct.

Submit your code via GitHub to receive credit for this assignment. Breaking all the passwords is not required to earn full credit for this assignment. See [Rubric](#rubric) for more details.

The program must exit gracefully in case of errors.

The assignment has a [GNUmakefile](https://en.wikipedia.org/wiki/Makefile) which you may use to build and test your progress. The GNUmakefile has the following targets:

* all: builds the project
* clean: removes object and dependency files
* spotless: removes everything the clean target removes and all binaries
* doc: generate HTML documentation from the source code using Doxygen
* format: outputs a [`diff`](https://en.wikipedia.org/wiki/Diff) showing where your formatting differes from the [Google C++ style guide](https://google.github.io/styleguide/cppguide.html)
* tidy: output of the [linter](https://en.wikipedia.org/wiki/Lint_(software)) to give you tips on how to improve your code
* headercheck: check to make sure your files have the appropriate header

To build the program use the `make` command. The GNUmakefile's default target is to build `all`. You must use the GNU version of `make` which is the default on Tuffix.

Every file that you submit must have a header. Please follow the guidelines from the course Canvas page.

Please adhere to the [Google C++ coding style](https://google.github.io/styleguide/cppguide.html).

When writing git log comments, please make them descriptive and meaningful.

# Example Output

Your program's output will not be reviewed. You may generate any kind of output you choose. Be aware that writing to the terminal is a very slow operation and will slow down your program.


# Rubric

There is a total of 10 points possible. Your program must compile before it is graded. _Submissions that do not compile shall be assigned a zero grade._

To earn full credit for this assignment, your submission must decrypt the easy passwords.

For each problem:

* Functionality (6 points): Your submission shall be assessed for the appropriate constructs and strategies to address the exercise. A program the passes the instructor's tests completely receives full marks. A program that partially passes the instructors tests receives partial-marks. A program that fails the majority or all the tests receives no marks. 
* Format & Readability (4 point): Your submission shall be assessed by checking whether your code passess the style and format check, as well as how well it follows the proper naming conventions, and internal documentation guidelines. Git log messages are an integral part of how readable your project is. Failure to include a header forfeits all marks. Failure to not conform to the [Google C++ coding style](https://google.github.io/styleguide/cppguide.html) forfeits all marks.
