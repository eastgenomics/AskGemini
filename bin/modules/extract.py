import argparse
import csv
from datetime import datetime

from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from sqlalchemy import (or_,and_)
class QuerySample:

    def __init__(self, name, depth, quality,AAF,allele_count):
        self.name = name
        self.depth = depth
        self.quality = quality
        self.allele_count = allele_count
        self.AAF = AAF

    def get_results(self):
        pass


class FrequencyOutput:

    def __init__(self, chrom,position,ref,alt,results,total_count):

        self.chrom = chrom
        self.position = position
        self.ref = ref
        self.alt = alt
        self.results = results
        self.total_count = total_count

    def set_output_folder(self):
        pass

    def get_output_name(self):

        now = datetime.now()

        results_file = str((now.isoformat()[:10])) + "_" + str(self.chrom) + "_" + \
                       str(self.position) + "_" + self.ref + "_" + self.alt + ".txt"

        return results_file

    def calculate_frequency(self):

        allele_count = 0
        for sample in self.results:
            allele_count = allele_count + sample.allele_count

        frequency = allele_count /( self.total_count*2)
        return frequency

def parse_arguments():
    parser = argparse.ArgumentParser(description = 'Extract information from GeminiDB')
    subparsers = parser.add_subparsers(dest = 'subparser_command', help='test test help me')

    freq_parser = subparsers.add_parser('calculate_geminiAF', help='Given a chromosomal position and'
                                                                  ' ref and alt calculates the frequency in GeminiDB')
    freq_parser.add_argument('Chrom', type = int, help= 'Enter the variant chromosome' )
    freq_parser.add_argument('Pos', type = int, help= 'Enter the variant position' )
    freq_parser.add_argument('Ref', type = str, help= 'Enter the reference allele' )
    freq_parser.add_argument('Alt', type = str, help= 'Enter the alternative allele' )

    panel_parser = subparsers.add_parser('get_panel_genes', help='Extracts all genes present in requested panel')
    panel_parser.add_argument('--panel', type = str, help='Enter Panel name')
    panel_parser.add_argument('-t',action='store_true',help= 'Returns Gene names with clinically active transcripts')
    panel_parser.add_argument('-s',action='store_true',help = 'Returns all sample for a panel')
    panel_parser.add_argument('--gene',type = str, help = 'Enter Gene name')


    arguments = parser.parse_args()


    return arguments


def get_variant_id(args):
    query_chrom = args.Chrom
    query_position = args.Pos
    query_ref = args.Ref
    query_alt = args.Alt

    # Get variant if=d for variant in question.
    qVariant = DBSession.query(Variant).filter_by(chrom=query_chrom, pos=query_position, ref=query_ref,
                                                  alt=query_alt)

    for result in qVariant:
        variant_result = result.id

    return variant_result

def find_samples_with_variant(variant_result):
    # Query database using variant_id in question
    analyses = DBSession.query(Analysis, AnalysisVariant).join(AnalysisVariant,
                                                               Analysis.id == AnalysisVariant.analysis_id).filter_by(
        variant_id=variant_result).join(Sample).order_by(Sample.name)

    query_results = []
    for a, av in analyses:
        result = QuerySample(a.sample.name, av.depth, av.quality, av.AAF, av.allele_count)
        query_results.append(result)

    return query_results


def get_frequency(args,query_results):
    total_count = DBSession.query(Sample).filter(or_(Sample.project_id == 1, Sample.project_id == 2)).count()
    print (total_count)
    frequency = FrequencyOutput(args.Chrom, args.Pos, args.Ref, args.Alt, query_results, total_count)
    output = frequency.get_output_name()
    gemini_AAF = frequency.calculate_frequency()

    return output,gemini_AAF

def write_to_file(output,gemini_AAF,query_results):
    with open(output, "+w") as out:
        output_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(['Sample', 'Depth', 'Qual', 'AAF', 'Allele_Count'])

        for variant in query_results:
            output_writer.writerow(
                [variant.name, variant.depth, variant.quality, variant.AAF, variant.allele_count])

        output_writer.writerow([])
        output_writer.writerow(['Gemini', 'Frequency', gemini_AAF])

    print("The frequency of the requested variant is :", round(gemini_AAF, 5))
    print('\n *** A .txt file containing the list of samples has been successfully created. ***')
    print("Filename: ", output)


def get_panel_id(args):

    panel_name = args.panel
    qPanel = DBSession.query(Panel).filter_by(name=panel_name)

    for result in qPanel:
        panel_id = result.id

    return panel_id


def get_gene_id(args):

    gene_name = args.gene
    qGene = DBSession.query(Gene).filter_by(name=gene_name)

    for result in qGene:
        gene_id = result.id

    return gene_id

def get_genes(panel_id):

    #qGenes = DBSession.query(GenePanel).join(Panel,Panel.id==GenePanel.panel_id)\
    #   .join(Gene, Gene.id == GenePanel.gene_id).filter(Panel.id==panel_id)

    qGenes = DBSession.query(Gene).join(GenePanel,GenePanel.gene_id == Gene.id)\
        .join(Panel,Panel.id == GenePanel.panel_id).filter(Panel.id == panel_id)

    genes = {}
    for entry in qGenes:
        genes[entry.id]=entry.name

    return genes

def get_transcripts(genes):

    transcripts = {}

    for key in genes.keys():
        g2t = DBSession.query(Transcript).join(Gene, Gene.id == Transcript.gene_id)\
            .filter(and_(Transcript.gene_id== key,Transcript.clinical_transcript=='Y'))
        for entry in g2t:
            transcripts[genes[key]] = entry.refseq

    return transcripts

def get_panels(gene_id):

    panels = []

    qPanels = DBSession.query(Panel).join(GenePanel,GenePanel.panel_id == Panel.id)\
        .join(Gene,GenePanel.gene_id == Gene.id).filter(Gene.id == gene_id)

    for entry in qPanels:
        panels.append(entry.name)

    return panels

def get_samples(panel_name):

    qSamples = DBSession.query(Sample).join(SamplePanel,SamplePanel.sample_id==Sample.id)\
        .filter(SamplePanel.panel_name == panel_name).order_by(Sample.name)

    samples = []
    for entry in qSamples:
        samples.append(entry.name)

    return samples

def panel_output(args,genes,transcripts,samples):

    if args.t:
        filename = args.panel + "_transcripts.txt"
        with open(filename, 'w+') as f:
            f.write("{}\n".format(args.panel))
            for key in transcripts.keys():
                f.write("{} \t {} \n".format(key, transcripts[key]))
    elif args.s:
        filename = args.panel + "_samples.txt"
        with open(filename, 'w+') as f:
            f.write("{} {}\n".format(args.panel,len(samples)))
            for sample in samples:
                f.write("{}\n".format(sample))
    else:
        filename = args.panel + ".txt"
        with open(filename, 'w+') as f:
            f.write("{}\n".format(args.panel))
            for key in genes.keys():
                f.write("{}\n".format(genes[key]))


def gene_output(args,panels):
    filename = args.gene + ".txt"

    with open (filename,'w+') as f:
        f.write("{}\n".format(args.gene))
        for panel in panels:
            f.write("{}\n".format(panel))

def main(args):


    if args.subparser_command == 'calculate_geminiAF':

        variant_result = get_variant_id(args)
        query_results = find_samples_with_variant(variant_result)
        output, gemini_AAF = get_frequency(args,query_results)
        write_to_file(output,gemini_AAF,query_results)

    elif args.subparser_command == 'get_panel_genes':


        if args.gene:
            gene_id = get_gene_id(args)
            panels = get_panels(gene_id)
            gene_output(args,panels)
        elif args.panel:
            panel_name = args.panel
            panel_samples = get_samples(panel_name)
            panel_id = get_panel_id(args)
            panel_genes = get_genes(panel_id)
            panel_transcripts = get_transcripts(panel_genes)
            panel_output(args,panel_genes,panel_transcripts,panel_samples)




if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
