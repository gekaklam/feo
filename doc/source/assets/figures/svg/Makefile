

%.eps: %.svg
	inkscape -f $< -E $@

all: $(addsuffix .eps, $(basename $(wildcard *.svg)))

clean:
	rm -rf *.eps
	rm *-eps-converted-to.pdf
