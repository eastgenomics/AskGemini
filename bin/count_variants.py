#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (December 2019) contact: adriana.toutoudaki@addenbrookes.nhs.uk

import argparse
from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from models import TranscriptRegion, Region
from sqlalchemy.sql.expression import func
from sqlalchemy import or_
from extract import get_gene_id, get_all_genes


class QueryRegion:

    def __init__(self,region_id,transcript, chrom, start,end, exon):
        self.region_id = region_id
        self.transcript = transcript
        self.chrom = chrom
        self.start = start
        self.end = end
        self.exon = exon
        self.range = range(self.start - 5, self.end + 6)

    def get_variant_ids(self):
        """
        Interogates DB to get the id of all the variant unique instances in the variant table

        :return: Single Nucleotide Variant ids, Indel IDs
        """

        qIndelInstances = DBSession.query(Variant).filter(
          Variant.chrom == self.chrom,Variant.pos>= self.start-5,Variant.pos<=self.end+5,or_(
          func.length(Variant.ref)>1,func.length(Variant.alt)>1))


        self.indel_ids = []
        for entry in qIndelInstances:
            self.indel_ids.append(entry.id)

        self.sv_ids = []
        qSVlInstances = DBSession.query(Variant).filter(
          Variant.chrom == self.chrom,Variant.pos>= self.start-5,Variant.pos<=self.end+5)

        for entry in qSVlInstances:
            self.sv_ids.append(entry.id)

        return self.sv_ids,self.indel_ids

    def get_variants(self):
        """
        Counts how many times all the unique variants per gene have been seen in out tested patients.
        :return: Count of single nucleotide variants, indel counts
        """
        qCountIndels = DBSession.query(AnalysisVariant).filter(AnalysisVariant.variant_id.in_(self.indel_ids), AnalysisVariant.quality >500).count()
        qCountSVs = DBSession.query(AnalysisVariant).filter(AnalysisVariant.variant_id.in_(self.sv_ids), AnalysisVariant.quality >500).count()

        return qCountSVs, qCountIndels


def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract information from GeminiDB')

    parser.add_argument('gene', type = str, help = 'Enter the gene name')
    parser.add_argument('--coordinates',action='store_true', help = 'only returns exon coordinates for given gene')

    args = parser.parse_args()

    return args


def get_transcript_id(gene_id):
    """
    Interrogates database to get the transcript id in question

    :param gene: str -- transcript name
    :return: Transcript id for the Clinically Relevant transcript (if there's two entries, it returns the 2nd one
    """

    qTranscript = DBSession.query(Transcript).filter_by(gene_id=gene_id).filter_by(clinical_transcript='Y')

    for result in qTranscript:
        transcript_id = result.id

    return transcript_id


def get_exon_coordinates(tr_id):
    """
    Interrogates transcript region and region tables to get exon boundaries for the gene requested
    :param tr_id:transcript id
    :return:
    """

    qTRegions = DBSession.query(TranscriptRegion,Region).join(Region, Region.id == TranscriptRegion.region_id )\
        .filter(TranscriptRegion.transcript_id==tr_id)

    regions = []
    for tr, r in qTRegions:
        query = QueryRegion(r.id,tr_id, r.chrom,r.start,r.end, tr.exon_nr)
        regions.append(query)


    return regions


def main(args):

    gene = (args.gene).upper()

    # Checks all gene, if gene not in the database it exits
    get_all_genes(gene)
    gene_id = get_gene_id(gene)

    transcript_id = get_transcript_id(gene_id)
    query_regions = get_exon_coordinates(transcript_id)

    # When coordinates argument present, only print the exon information.
    if args.coordinates:
        print(gene)
        print((' ').join(["Exon", "Chrom", "Start", "End"]))

        for exon in query_regions:
            print (exon.exon, exon.chrom,exon.start,exon.end)
        exit()

    unique_SVs = 0
    unique_INDELS = 0
    SVs = 0
    INDELS = 0

    # Each exon is stored in a QueryRegion instance, this loop goes over all exon and sums the variants for the gene.
    for region in query_regions:
        uSV,uIndel = region.get_variant_ids()
        SV,Indel = region.get_variants()

        unique_SVs += len(uSV)
        unique_INDELS += len(uIndel)
        SVs += SV
        INDELS += Indel

    print ('\nVariants in in GeminiDB\n------------------------------')
    print ('{}\tTotal\tUnique'.format(gene))
    print ('SVs\t{}\t{}'.format(SVs,unique_SVs))
    print ('Indels\t{}\t{}'.format(INDELS,unique_INDELS))


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)



