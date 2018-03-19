rudix.pdf: rudix.1
	groff  -Tps  -mandoc -c rudix.1 > rudix.ps
	pstopdf rudix.ps -o rudix.pdf

clean:
	rm -f *~ *.pdf *.ps

.PHONY: clean
