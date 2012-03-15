# OpaBDDC. (c) Valdabondance.com 2011
# @author Matthieu Guffroy, Thomas Recouvreux

OPA=opa
EXE=main.exe
DATABASE=db3
OPT=-o $(EXE) --database $(DATABASE)
DEBUG=--debug-editable-css --verbose 100
FILES=$(shell find src -name '*.opa')
RUN-OPT=--db-force-upgrade #--db-remote localhost:27017 #--db-force-upgrade #--db-local db/db --db-force-upgrade


#-----------------------------------------------#
#-----------------------------------------------#
#		COMPILATION			#
#-----------------------------------------------#
#-----------------------------------------------#


all: $(FILES)
	$(OPA) $(OPT) $^




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
	rm -rf _build
	rm -f *.exe
	rm -rf doc
	rm -rf _tracks
	rm -f *.log
	rm -rf *.opp

help:
	cat Makefile.help

