#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019)
# contact: adriana.toutoudaki@addenbrookes.nhs.uk

#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019)
# contact: adriana.toutoudaki@addenbrookes.nhs.uk

import argparse
import csv
#from datetime import datetime
from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from models import TranscriptRegion, Region
from sqlalchemy import (or_,and_,exists)
from extract import get_gene_id

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract information from GeminiDB')

    parser.add_argument('gene', type = str, help = 'Enter the gene name')
    parser.add_argument('--coordinates',action='store_true', help = 'only returns exon coordinates for given gene')

    args = parser.parse_args()

    return args




def get_transcript_id(gene_id):
    """
    Interrogates database to get gene id in question

    :param gene: str -- gene name
    :return: Gene if from gene table
    """

    qTranscript = DBSession.query(Transcript).filter_by(gene_id=gene_id).filter_by(clinical_transcript='Y')

    for result in qTranscript:
        transcript_id = result.id

    return transcript_id


def get_exon_coordinates(tr_id):

    qTRegions = DBSession.query(TranscriptRegion).join(Region, Region.id == TranscriptRegion.region_id )\
        .filter(TranscriptRegion.transcript_id==tr_id)

    regions = {}
    for entry in qTRegions:
        print (entry)

def get_genes(panel_id):
    for key in genes.keys():
        g2t = DBSession.query(Transcript).join(Gene, Gene.id == Transcript.gene_id)\
            .filter(and_(Transcript.gene_id== key,Transcript.clinical_transcript=='Y'))
        for entry in g2t:
            transcripts[genes[key]] = entry.refseq

    return transcripts


def main(args):
    gene = (args.gene).upper()
    gene_id = get_gene_id(gene)

    transcript_id = get_transcript_id(gene_id)

    get_exon_coordinates(transcript_id)


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)



