# OpaBDDC. (c) Valdabondance.com 2011
# @author Matthieu Guffroy, Thomas Recouvreux

OPA=opa
OPA_PLUGIN_BUILDER=opa-plugin-builder
OPADOC=opadoc
BUILD_DIR=_build
OPT=--opx-dir $(BUILD_DIR)
OPT-RELEASE=$(OPT) --compile-release
PLUGIN_OPT=
DEBUG=--debug-editable-css --verbose 100
FILES=$(shell find src -name '*.opa')
EXE=main.exe
RUN-OPT=--db-force-upgrade #--db-local db/db --db-force-upgrade


#-----------------------------------------------#
#-----------------------------------------------#
#		COMPILATION			#
#-----------------------------------------------#
#-----------------------------------------------#


all: $(FILES)
	$(OPA) $^ -o main.exe $(OPT)




#-----------------------------------------------#
#-----------------------------------------------#
#		RUN				#
#-----------------------------------------------#
#-----------------------------------------------#

run:
	./$(EXE) $(RUN-OPT)

run-debug: all
	./$(EXE) $(RUN-OPT) $(DEBUG)





#-----------------------------------------------#
#-----------------------------------------------#
#		CLEAN				#
#-----------------------------------------------#
#-----------------------------------------------#


clean-db:
	rm -rf db/*

clean:
	rm -rf $(BUILD_DIR)/*
	rm -f *.exe
	rm -rf doc
	rm -rf _tracks
	rm -f *.log
	rm -rf *.opp

help:
	cat Makefile.help

