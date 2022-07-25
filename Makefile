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

TARGET = brute
# C++ Files
CXXFILES = brute.cc
HEADERS = 

CXX = g++
CFLAGS += -g -O3 -Wall -pipe -std=c++14
LDFLAGS += -g -O3 -Wall -pipe -std=c++14
LDLIBS += -lcrypt

UNAME_S = $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	CFLAGS += -mmacosx-version-min=11.3
	LDFLAGS += -mmacosx-version-min=11.3
	LDLIBS=
endif

FORMAT = clang-format
FORMATFLAGS = -style=Google --Werror

TIDY = clang-tidy
TIDYFLAGS = "-checks=-*,google-*,modernize-*,readability-*,\
						 cppcoreguidelines-*,-google-build-using-namespace,\
						 -modernize-use-trailing-return-type,\
						 -cppcoreguidelines-avoid-magic-numbers,\
						 -readability-magic-numbers,\
						 -cppcoreguidelines-pro-type-union-access,\
						 -cppcoreguidelines-pro-bounds-constant-array-index,\
						 -cppcoreguidelines-pro-bounds-pointer-arithmetic"

DOXYGEN = doxygen
DOCDIR = doc

OBJECTS = $(CXXFILES:.cc=.o)

DEP = $(CXXFILES:.cc=.d)

.SILENT: tidy format headercheck

default all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(LDFLAGS) -o $(TARGET) $(OBJECTS) $(LDLIBS)

-include $(DEP)

%.d: %.cc
	set -e; $(CXX) -MM $(CFLAGS) $< \
	| sed 's/\($*\)\.o[ :]*/\1.o $@ : /g' > $@; \
	[ -s $@ ] || rm -f $@

%.o: %.cc
	$(CXX) $(CFLAGS) -c $<

clean:
	-rm -f $(OBJECTS) core $(TARGET).core

spotless: clean
	-rm -f $(TARGET) $(DEP) a.out
	-rm -rf $(DOCDIR)
	-rm -rf $(TARGET).dSYM
	-rm -f compile_commands.json

doc: $(CXXFILES) $(HEADERS)
	$(DOXYGEN) Doxyfile

format:
	echo "Lines starting with '<' are from your file."
	echo "Lines starting with '>' are what you should have written"
	echo "  according to the Google C++ Style Guide."
	$(eval FORMATOUT := $(shell mktemp))
	for i in $(CXXFILES) $(HEADERS); do \
		echo "Checking $$i"; \
		$(FORMAT) $(FORMATFLAGS) $$i > $(FORMATOUT); \
		diff $$i $(FORMATOUT) || \
			echo "\nYour file does not conform to the Google C++ Style." \
			"Please edit your code until this message is removed.\n"; \
			rm $(FORMATOUT); \
	done

tidy:
	.action/mkcompiledb.py
	for i in $(CXXFILES) $(HEADERS); do \
		echo "Checking $$i"; \
		$(TIDY) $$i $(TIDYFLAGS) ; \
	done

headercheck:
	for i in $(CXXFILES) $(HEADERS); do \
		echo "Checking $$i header"; \
		.action/header_check.py $$i; \
	done
