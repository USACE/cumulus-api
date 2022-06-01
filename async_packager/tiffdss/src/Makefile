HECDSS := /hec-dss

LIB := tiffdss
BUILD_DIR := ./Output
SRC_DIRS := ./src
RM = rm -fr
HLIBC = /hec-dss/heclib/heclib_c/Output/libhec_c.a
HLIBF = /hec-dss/heclib/heclib_f/Output/libhec_f.a
HLIB := $(HLIBC) $(HLIBF)

CC = gcc
CFLAGS = -m64 -c -fPIC -g -std=gnu99 -D__linux__
LDFLAGS = -lgdal -lgfortran -lm -lz
CWARNING = -Werror -Wno-unused-result
HEADERS = -I/hec-dss/heclib/heclib_c/src/headers


# Build DSS C
# SRCS := $(shell find /hec-dss/heclib/heclib_c/src -name '*.c' )

# OBJS := $(SRCS:%=/hec-dss/heclib/heclib_c/Output/%.o)

# /hec-dss/heclib/heclib_c/Output/libhec_c.a: $(OBJS)
# 	$(AR) -r $@  $(OBJS)  

# /hec-dss/heclib/heclib_c/Output/%.c.o: %.c
# 	mkdir -p $(dir $@)
# 	$(CC) $(CFLAGS) -c $< -o $@




# tiffdss: tiffdss.o utils.o
# 	$(CC) $^ $(HLIB) $(HLIB) $(LDFLAGS) -o $@

# libtiffdss.so: tiffdss.o utils.o
# 	$(CC) tiffdss.o utils.o $(HLIB) $(HLIB) $(LDFLAGS) -shared -o $@

# main.o: main.c
# 	$(CC) $(CFLAGS) -o $@ -c $<

# tiffdss.o utils.o: %.o: %.c
# 	$(CC) $(CFLAGS) $(HEADERS) $(CWARNING) -o $@ -c $<

# .PHONY: clean
# clean:
# 	$(RM) *.o


