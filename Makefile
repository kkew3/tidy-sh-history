.PHONY: all clean

all: unmetafy

unmetafy: unmetafy.c
	clang -o $@ $^

clean:
	rm -f unmetafy
