CC = clang


.PHONY: all clean

all: unmetafy

unmetafy: unmetafy.c
	$(CC) -o $@ $^

clean:
	rm -f unmetafy
