.. _seqal_index:

Seqal
======


Seqal is a distributed short read mapping and duplicate removal tool.
It implements a distributed version of the BWA_ aligner, and adds a duplicate
read identification feature using the same criteria as the `Picard MarkDuplicates`_ 
command (see below for details).

Usage
++++++

Like BWA, Seqal takes as input read pairs to be aligned, and an indexed
reference sequence.  The input read pairs need to be in :ref:`prq format <file_formats_prq>` (PairReadsQSeq
may help you format them quickly), and they need to be located on an HDFS
volume. The indexed reference is a slightly modified version of the one
generated by BWA.  See the following section for instructions.

Preparing the reference index archive
-------------------------------------

Seqal needs a modified version of the BWA index files to run.  The original
index must be generated with a compatible version of BWA.  To created the
modified index follow these steps:

#. Generate the standard bwa index::

    bwa index [OPTIONS] ref.fa

#. Modify it::

    ./bin/seal_bwa_index_to_mmap ref.fa

   This generates two new files:  ref.fa.sax and ref.fa.rsax.

#. Delete the original ``.sa`` and ``.rsa`` files::

    rm -f ref.fa.*sa

   These two files are not required by Seqal.

#. Build an archive containing the index files at the top level::

    tar cf ref.tar ref.fa.*

Hadoop's distributed cache mechanism will be used to distribute and unpack the
archive on all the cluster nodes.  We recommend not including the original
``.sa`` and ``.rsa`` files since for a full human genome reference they are
large enough to slow the distribution process by a few minutes.  Also, we
recommend not compressing the archive since we have found that decompressing it
adds several minutes to the start-up time, even if copying the file may be
faster.  Using a light compression (e.g. ``gzip --fast``) may be the optimal
solution but we have yet to test it.


BWA index version compatibility
.....................................

============= ==========================
Seal version   BWA version
============= ==========================
0.2.2 --       0.5.10
0.1 -- 0.2.1   0.5.9
============= ==========================



Running the application
-----------------------

To run seqal, use the ``bin/seal_seqal`` command::

  bin/seal_seqal INPUT OUTPUT REF.tar

The command takes the following arguments:

#. Input path (a file or a directory), containing paired sequence data in prq
   format.  If the path references a directory, then all the files inside it
   will be processed.

#. Output directory, where results in SAM format will be written.

#. Reference index archive (see previous section).



Command line options
.......................

======= ============= =========================================================
 Short  Long           Description
======= ============= =========================================================
 -q Q   --trimq Q     trim quality, like BWA's -q argument (default: 0).    
 -a     --align-only  Only perform alignment and skip duplicates detection  
                      (default: false).                                     
======= ============= =========================================================

Seqal also provides a number of properties to control its behaviour.
For a full description see the :ref:`seqal_options` page.

In addition to the mandatory arguments and options listed here, Seqal supports
the usual Seal command line options.  See the :ref:`program_usage` section for
details.


Criteria for duplicate reads
++++++++++++++++++++++++++++++

The criteria applied by Seqal (and by Picard at the time of this writing)
to identify duplicate reads roughly equates to aligned finding fragments
that start and end at the same reference position.  

These are the steps that explain the criteria in more detail.

1. Find the mapping orientation for each read
----------------------------------------------

Each read can be mapped on the forward or reverse strand.


2. Find start and end reference coordinates for sequenced fragment
---------------------------------------------------------------------

We want to find the *reference* positions of the "edges" of each sequenced
fragment.  To do this, we find the 5' (left-most) reference position of each
read aligned to the forward strand and the 3' (right-most) reference position of
each read aligned to the reverse strand.  This step has to consider any read
clipping that may have been done in alignment, as well as insertions and
deletions with respect to the reference sequence.

Example
..........


Take a single fragment that we're going to sequence::

             AAACCCGGGTTTAAAGTTCAAGCAATTCTCACCTCCACCTTCCAGAACCGGTTAACCGGT
  sequence   |------------>|                              |<------------|
                 Read 1                                        Read 2

The sequencer reads Read 1 and Read 2 from the outside of the fragment inwards.
It then reverses the second read so that both reads are presented to us as if we
were looking from the "left" side of the fragment above::

             S                                            E
             AAACCCGGGTTTAAA                              TGGCCAATTGGCCAA
             |------------>|                              |------------>|
                 Read 1                                        Read 2

*S* is the fragment start and *E* is the fragment end.


Now we map these reads to a reference.

Suppose both reads align to the forward strand.  In this case the aligner gives
us the reference coordinate of the left-most base::

       pos                                          pos
       |                                            |
       V                                            V
       AAACCCGGGTTTAAA                              TGGCCAATTGGCCAA
       S                                            E

So, in this case, the alignment positions are actually the positions of first
and last bases of the original fragment.


Suppose now that read 2 is mapped to the reverse strand.  The read is reversed
and complemented in the SAM record.

::

       pos                                          pos
       |                                            |
       V                                            V
       AAACCCGGGTTTAAA                              TTGGCCAATTGGCCA
       S                                                          E

Since the second read has been reversed, the end of the fragment now corresponds to
read 2's last base.  Therefore, we have to find its reference position by
looking at the alignment start position and the CIGAR operators.
We have an analogous case when Read 1 is aligned to the reverse strand.

Not all CIGAR operators are equal of course.  To calculate the reference
position of the last base of the read, we begin with the alignment position and
then slide it down the reference with each operation that "consumes" reference
bases (e.g. Match, Delete, etc.).  For instance, the last base of a read aligned
on chromosome 1 at position 1234, with CIGAR 17M1D74M, would be at position::

  1234 + 17 + 1 + 74 - 1 = 1325

The '-1' is to avoid going one position past the end of the read.

On the other hand, a read at position 1234 with CIGAR 15S22M1I63M would have its
last base at::

  1234 + 22 + 63 - 1 = 1318

Notice that we skip the soft clipped bases (the alignment position in the SAM
refers to the first unclipped base on the 5' side) and that we also skip the
insertion, since that base on the read has no corresponding base on the
reference.




3. Find pairs with identical read coordinates and orientation
----------------------------------------------------------------------------

Using the information calculated in the previous two steps, find all pairs that
have identical adjusted coordinates (as in step 2) and mapping orientation for
both read and mate.  With this criteria we identify sets of equivalent reads.
Given a set, leave the pair with the highest base qualities as is, while we label
the rest as duplicates.

To decide which pair has the best quality, we sum all base qualities >= 15.  The
pair with the highest sum "wins".

4. Identify duplicate unpaired reads
----------------------------------------

For unpaired reads (or reads whose mate is unmapped), if the read's adjusted
coordinate (as in step 2) falls on a coordinate where we found a paired read, it
will be marked as a duplicate---i.e.  paired reads are given precedence.

If instead for a particular coordinate and orientation we only find unpaired
reads, then we apply the same base quality-based criteria that we used for
pairs:  the one with the highest ``sum( base qualities >= 15 )`` base quality is left
as is, while the rest are marked as duplicates.

Unmapped reads
--------------------

Unmapped reads cannot be marked as duplicates, since our criteria for
identifying duplicates is based on mapping coordinates.  Seqal does not try to
match reads by identical nucleotide sequence.



.. _BWA:  http://bio-bwa.sourceforge.net/
.. _Picard MarkDuplicates:  http://sourceforge.net/apps/mediawiki/picard/index.php?title=Main_Page#Q:_How_does_MarkDuplicates_work.3F
.. _BWA manpage: http://bio-bwa.sourceforge.net/bwa.shtml
