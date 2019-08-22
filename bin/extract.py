import argparse
import csv
from datetime import datetime

from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from sqlalchemy import (or_,and_)

class QuerySample:
    """object that contains fields that get exported """

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
        """
        Creates the filename for the list of samples including the frequency calculated.
        :return: Result filename timestamped and including the query information
        """

        now = datetime.now()

        results_file = str((now.isoformat()[:10])) + "_" + str(self.chrom) + "_" + \
                       str(self.position) + "_" + self.ref + "_" + self.alt + ".txt"

        return results_file

    def calculate_frequency(self):
        """
        Calculates frequency of requested variant, by divided the sum of allele counts of the vatiants identified,
        divided by the total number of samples in GeminiDB multiplied by two.
        :return: variant frequency
        """

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


def get_variant_id(chrom,pos,ref,alt):
    """
    Retrieves variant id from GeminiDB.

    :param chrom: int -- variant chromosome number
    :param pos: int -- variant position
    :param ref: str -- reference base
    :param alt: str -- reference alternative base
    :return: Returns variant id from the Variant table.
    """

    # Query Variant table in database
    qVariant = DBSession.query(Variant).filter_by(chrom=chrom, pos=pos, ref=ref,
                                                  alt=alt)
    # Returns an object list so need to loop through to access the entry.
    for result in qVariant:
        variant_result = result.id

    return variant_result


def find_samples_with_variant(variant_result):
    """
    Extract the sample names and variant sequencing information.

    :param variant_result: variant id
    :return: List of QuerySample objects containing sample name and metrics
    """
    # Query database using variant_id in question.
    # Sample table joins to analysis table, and analysis to analysis variant.
    analyses = DBSession.query(Analysis, AnalysisVariant).join(AnalysisVariant,
                                                               Analysis.id == AnalysisVariant.analysis_id).filter_by(
        variant_id=variant_result).join(Sample).order_by(Sample.name)

    query_results = []
    # a for analysis and av for analysis variant.
    for a, av in analyses:
        result = QuerySample(a.sample.name, av.depth, av.quality, av.AAF, av.allele_count)
        query_results.append(result)

    return query_results


def get_frequency(chrom,pos,ref,alt,query_results):
    """
    Calculates the frequency of a variant in the Gemini Database

    :param chrom: int -- variant chromosome number
    :param pos: int -- variant position
    :param ref: str -- reference base
    :param alt: str -- reference alternative base
    :param query_results: List of objects containing sample name and variant metrics.
    :return: Output filename(str) and frequency result(float)
    """

    # Get the total number of G(1) and X(2) samples.
    total_count = DBSession.query(Sample).filter(or_(Sample.project_id == 1, Sample.project_id == 2)).count()
    frequency = FrequencyOutput(chrom,pos,ref,alt, query_results, total_count)
    output = frequency.get_output_name()
    gemini_aaf = frequency.calculate_frequency()

    return output,gemini_aaf


def write_to_file(output,gemini_aaf,query_results):
    """
     Writes output file containing sample list with variant metrics and the calculated frequency,

    :param output:str -- filename for output
    :param gemini_AAF: float -- frequency result
    :param query_results: List of objects containing sample name and variant metrics.
    """
    with open(output, "+w") as out:
        output_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(['Sample', 'Depth', 'Qual', 'AAF', 'Allele_Count'])

        for variant in query_results:
            output_writer.writerow(
                [variant.name, variant.depth, variant.quality, variant.AAF, variant.allele_count])

        output_writer.writerow([])
        output_writer.writerow(['Gemini', 'Frequency', gemini_aaf])

    print("The frequency of the requested variant is :", round(gemini_aaf, 5))
    print('\n *** A .txt file containing the list of samples has been successfully created. ***')
    print("Filename: ", output)


def get_panel_id(panel):
    """
    Interrogates database to get panel id from Panel table.

    :param panel: str - name of panel (has to be exactly the same as the one in the database)
    :return: int -- panel table id for requested panel
    """

    qPanel = DBSession.query(Panel).filter_by(name=panel)

    for result in qPanel:
        panel_id = result.id

    return panel_id


def get_gene_id(gene):
    """
    Interrogates database to get gene id in question

    :param gene: str -- gene name
    :return: Gene if from gene table
    """

    qGene = DBSession.query(Gene).filter_by(name=gene)

    for result in qGene:
        gene_id = result.id

    return gene_id

def get_genes(panel_id):
    """
    Finds the genes included in the requested panel

    :param panel_id: int -- id of panel
    :return: Dict of genes with gene ids as keys and gene names as values
    """

    # Queries the database.
    # Gene to Panels have a many to many relationship which requires the GenePanel table as an association table

    qGenes = DBSession.query(Gene).join(GenePanel,GenePanel.gene_id == Gene.id)\
        .join(Panel,Panel.id == GenePanel.panel_id).filter(Panel.id == panel_id)

    genes = {}
    for entry in qGenes:
        genes[entry.id]=entry.name

    return genes


def get_transcripts(genes):
    """
    Returns transcripts for genes present in the panel

    :param genes: dict -- {gene_id:gene_name}
    :return: dict -- transcript dictionary with gene names as keys and refseq transcripts as values
    """
    transcripts = {}

    for key in genes.keys():
        g2t = DBSession.query(Transcript).join(Gene, Gene.id == Transcript.gene_id)\
            .filter(and_(Transcript.gene_id== key,Transcript.clinical_transcript=='Y'))
        for entry in g2t:
            transcripts[genes[key]] = entry.refseq

    return transcripts

def get_panels(gene_id):
    """
    Returns list of panels a specific gene is in

    :param gene_id: int -- id of gene
    :return: list -- panel names
    """

    panels = []

    qPanels = DBSession.query(Panel).join(GenePanel,GenePanel.panel_id == Panel.id)\
        .join(Gene,GenePanel.gene_id == Gene.id).filter(Gene.id == gene_id)

    for entry in qPanels:
        panels.append(entry.name)

    return panels

def get_samples(panel):
    """
    Creates a list of samples that have been tested for a specific panel

    :param panel: str -- panel name
    :return: list of samples
    """

    qSamples = DBSession.query(Sample).join(SamplePanel,SamplePanel.sample_id==Sample.id)\
        .filter(SamplePanel.panel_name == panel).order_by(Sample.name)

    samples = []
    for entry in qSamples:
        samples.append(entry.name)

    return samples

def panel_output(args,genes,transcripts,samples):

    """
    Writes appropriate file depending on the argument used

    :param args: arguments parsed
    :param genes: dict of genes
    :param transcripts: dict of transcripts
    :param samples: list of samples

    """

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


def gene_output(gene,panels):
    """
    Writes file when list of panels tested is requested.

    :param gene: str - gene name
    :param panels: list of panels

    """
    filename = gene + ".txt"

    with open (filename,'w+') as f:
        f.write("{}\n".format(gene))
        for panel in panels:
            f.write("{}\n".format(panel))


def main(args):

    if args.subparser_command == 'calculate_geminiAF':

        chrom = args.Chrom
        pos = args.Pos
        ref = args.Ref
        alt = args.Alt

        variant_result = get_variant_id(chrom,pos,ref,alt)
        query_results = find_samples_with_variant(variant_result)
        output, gemini_AAF = get_frequency(chrom,pos,ref,alt,query_results)
        write_to_file(output,gemini_AAF,query_results)

    elif args.subparser_command == 'get_panel_genes':

        if args.gene:
            gene = args.gene
            gene_id = get_gene_id(gene)
            panels = get_panels(gene_id)
            gene_output(gene,panels)
        elif args.panel:
            panel = args.panel
            panel_samples = get_samples(panel)
            panel_id = get_panel_id(panel)
            panel_genes = get_genes(panel_id)
            panel_transcripts = get_transcripts(panel_genes)
            panel_output(args,panel_genes,panel_transcripts,panel_samples)


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
