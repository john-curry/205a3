SRC=$(wildcard *.py) 
ARG=trees/sample_tree1.txt
all: $(SRC);python -B $< $(ARG)

%.py:
