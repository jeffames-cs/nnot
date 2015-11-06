DATAFILES=training.data testing.data

.PHONY: all clean

all: $(DATAFILES) objtrack.net

%.net: $(DATAFILES)
	./ann.py

%.data:
	./generate-data.py > $@

clean:
	@rm -f $(DATAFILES)
