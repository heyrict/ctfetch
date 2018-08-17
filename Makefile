MAIN=ctfetch.py
PRG=ctfetch

.PHONY: clean

install: $(MAIN)
	cp $(MAIN) /usr/local/bin/$(PRG)

clean:
	rm /usr/local/bin/$(PRG)
