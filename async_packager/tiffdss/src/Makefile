CC = gcc
RM = rm -fr
CFLAGS = -m64 -c -fPIC -g -std=gnu99 -D__linux__
HECFLAG = -lhec_c -lhec_f
LDFLAGS = -lgdal -lgfortran -lm -lz
CWARNING = -Werror -Wno-unused-result

# define header paths to search in
export CPATH := /hec-dss/heclib/heclib_c/src/headers

tiffdss : tiffdss.o utils.o
	$(CC) $^ $(HECFLAG) $(HECFLAG) $(LDFLAGS) -o $@

libtiffdss.so: tiffdss.o utils.o
	$(CC) tiffdss.o utils.o $(HECFLAG) $(HECFLAG) $(LDFLAGS) -shared -o $@

%.o: %.c
	$(CC) $(CFLAGS) $(CWARNING) -o $@ -c $<

.PHONY: clean
clean:
	$(RM) *.o
