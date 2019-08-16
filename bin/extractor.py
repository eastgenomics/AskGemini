#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019), contact: adriana.toutoudaki@addenbrookes.nhs.uk

import argparse
import csv
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session,sessionmaker,relationship
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Sequence,
    Float,
    MetaData,
    Enum,
    func, or_
)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Sample(Base):
    __tablename__ = "sample"
    id = Column(Integer,primary_key=True)
    project_id = Column(Integer)
    name = Column(String(80))
    labid = Column(String(80))
    first_name = Column(String(80))
    last_name = Column(String(80))

    analyses = relationship("Analysis", back_populates="sample")


class Analysis(Base):
    __tablename__="analysis"
    id = Column(Integer,primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.id'))
    runfolder_id = Column(Integer)
    reference_id = Column(Integer)
    status = Column(String(80))
    total_reads = Column(Integer)
    mapped_reads = Column(Integer)
    duplicate_reads = Column(Integer)
    mean_isize = Column(Float)
    mean_het_ratio = Column(Float)
    mean_homo_ratio = Column(Float)
    gender = Column(Enum('F', 'M', 'U'))
    capture = Column(String(80))
    bases_on_target = Column(Float)
    mean_target_coverage = Column(Float)
    coverage_0x = Column(Float)
    coverage_2x = Column(Float)
    coverage_10x = Column(Float)
    coverage_20x = Column(Float)
    coverage_30x = Column(Float)
    coverage_40x = Column(Float)
    coverage_50x = Column(Float)
    coverage_100x = Column(Float)
    versions = Column(String(2000))

    sample = relationship("Sample", foreign_keys = [sample_id])

    analysis_variants = relationship("AnalysisVariant", back_populates = "analysis")


class Variant(Base):
    __tablename__=  "variant"
    id = Column(Integer,primary_key=True)
    reference_id = Column(Integer)
    chrom = Column(String(8))
    pos = Column(Integer)
    ref = Column(String(100))
    alt = Column(String(100))
    comment = Column(String(200))

    a_variants = relationship("AnalysisVariant", back_populates= "variant")


class AnalysisVariant(Base):
    __tablename__ = "analysis_variant"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer,ForeignKey('analysis.id'))
    variant_id = Column(Integer,ForeignKey('variant.id'))
    depth = Column(Integer)
    AAF = Column(Float)
    quality = Column(Float)
    GQ = Column(Float)
    allele_count = Column(Integer)
    phase_key = Column(String(20))

    analysis = relationship("Analysis", foreign_keys = [analysis_id],backref="test_analysis")
    variant = relationship("Variant", foreign_keys = [variant_id],backref="test_variants")


class Panel(Base):
    __tablename__ = "panel"
    id = Column(Integer,primary_key = True)
    name = Column(String(200))
    ext_id = Column(Integer)
    active = Column(Enum('Y','N'))


class Gene(Base):
    __tablename__ = "gene"
    id = Column(Integer,primary_key = True)
    name = Column(String(80))
    hgnc = Column(Integer)


class GenePanel(Base):
    __tablename__ = "gene_panel"
    id = Column(Integer, primary_key=True)
    panel_id = Column(Integer,ForeignKey('panel.id'))
    gene_id = Column(Integer,ForeignKey('gene.id'))


class QuerySample:

    def __init__(self, name, depth, quality, allele_count,AAF):
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
    panel_parser.add_argument('Panel', type = str, help='Enter Panel name')

    arguments = parser.parse_args()


    return arguments


def get_variant_if():
    pass


def main(args):

    # set up the engine
    ConnectionString = "mysql://ga_ro:readonly@sql01/genetics_ark_1_1_0"
    # echo=True makes the sql commands issued by sqlalchemy get output to the console, useful for debugging
    # engine = create_engine(ConnectionString, echo=True)
    engine = create_engine(ConnectionString)
    # bind the dbsession to the engine
    DBSession.configure(bind=engine)
    # now you can interact with the database if it exists
    # import all your models then execute this to create any tables that don't yet exist.This does not handle migrations
    Base.metadata.create_all(engine)

    if args.subparser_command == 'calculate_geminiAF':
        query_chrom = args.Chrom
        query_position = args.Pos
        query_ref = args.Ref
        query_alt = args.Alt

        # Get variant if=d for variant in question.
        qVariant = DBSession.query(Variant).filter_by(chrom=query_chrom, pos=query_position, ref=query_ref,
                                                      alt=query_alt)

        for result in qVariant:
            variant_result = result.id

        # Query database using variant_id in question
        analyses = DBSession.query(Analysis, AnalysisVariant).join(AnalysisVariant,
                                                                   Analysis.id == AnalysisVariant.analysis_id).filter_by(
            variant_id=variant_result).join(Sample).order_by(Sample.name)

        query_results = []
        for a, av in analyses:
            result = QuerySample(a.sample.name, av.depth, av.quality, av.AAF, av.allele_count)
            query_results.append(result)

        # get total number of samples run
        qCount = DBSession.query(Sample).filter(or_(Sample.project_id == 1, Sample.project_id == 2)).count()

        frequency = FrequencyOutput(query_chrom, query_position, query_ref, query_alt, query_results, qCount)
        output = frequency.get_output_name()
        gemini_AAF = frequency.calculate_frequency()

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

    elif args.subparser_command == 'get_panel_genes':
        print(args.Panel)


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)

