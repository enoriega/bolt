#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import os, subprocess
from glob import glob
from boltdata import read_output



lattice_tool = '/home/marcov/tools/srilm/bin/i686-m64/lattice-tool'


names, refs, hyps, sausages, lattices, nbest = read_output()
for s,l in zip(sausages, lattices):
    s = s.replace('aligned_sausages', 'sausages')
    filename = os.path.basename(s)
    outdir = os.path.dirname(os.path.dirname(s))
    outdir = os.path.join(outdir, 'aligned_sausages')
    outfile = os.path.join(outdir, filename)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    subprocess.call([lattice_tool, '-read-htk', '-in-lattice', l,
                     '-init-mesh', s, '-write-mesh', outfile,
                     '-acoustic-mesh'])
    print outfile

