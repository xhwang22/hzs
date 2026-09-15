# Overleaf runs latexmk, not the local Makefile. Make the vendored ICLR
# package and BibTeX style visible while retaining the default TeX paths.
$ENV{'TEXINPUTS'} = './vendor/iclr2027//:' . ($ENV{'TEXINPUTS'} // '') . ':';
$ENV{'BSTINPUTS'} = './vendor/iclr2027//:' . ($ENV{'BSTINPUTS'} // '') . ':';
