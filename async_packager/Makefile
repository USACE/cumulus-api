HECLIB_C := /hec-dss/heclib/heclib_c
HECLIB_F := /hec-dss/heclib/heclib_f
TIFFDSS := /tiffdss/src

BUILD_DIR := Output

# export to override the variable in the heclib_f make
export FDEBUG = -fcheck=all,no-recursion -fallow-argument-mismatch

.PHONY: build cbuild fbuild

build: cbuild fbuild

cbuild: $(HECLIB_C)
	$(MAKE) clean -C $<
	$(MAKE) -C $<

fbuild: $(HECLIB_F)
	$(MAKE) clean -C $<
	$(MAKE) -C $<

# tiff: $(TIFFDSS)
# 	$(MAKE) clean -C $<
# 	$(MAKE) -C $<
