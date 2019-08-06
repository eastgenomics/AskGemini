#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019), contact: adriana.toutoudaki@addenbrookes.nhs.uk

import argparse

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
    Enum
)
import datetime


parser = argparse.ArgumentParser(description = 'Calculate gemini variant frequnecy')
parser.add_argument('Chrom', type = int, help= 'Enter the variant chromosome' )
parser.add_argument('Pos', type = int, help= 'Enter the variant position' )
parser.add_argument('Ref', type = str, help= 'Enter the reference allele' )
parser.add_argument('Alt', type = str, help= 'Enter the alternative allele' )
args = parser.parse_args()

query_chrom = args.Chrom
query_position = args.Pos
query_ref = args.Ref
query_alt = args.Alt

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Sample(Base):
    __tablename__ = "sample"
    id = Column(Integer,primary_key=True)
    project_id = Column(Integer)
    name = Column(String(80))
    labid = Column(String(80))
    fist_name = Column(String(80))
    last_name = Column(String(80))


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

    sample = relationship("Sample", git = [sample_id])


class Variant(Base):
    __tablename__=  "variant"
    id = Column(Integer,primary_key=True)
    reference_id = Column(Integer,ForeignKey('reference.id'))
    chrom = Column(String(8))
    pos = Column(Integer)
    ref = Column(String(100))
    alt = Column(String(100))
    comment = Column(String(200))


class AnalysisVariant(Base):
    __tablename__ = "analysis"
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


def main():
    # set up the engine
    ConnectionString = "mysql://ga_ro:readonly@sql01/genetics_ark_1_1_0"
    # echo=True makes the sql commands issued by sqlalchemy get output to the console, useful for debugging
    engine = create_engine(ConnectionString, echo=True)

    # bind the dbsession to the engine
    DBSession.configure(bind=engine)

    # now you can interact with the database if it exists
    # import all your models then execute this to create any tables that don't yet exist.This does not handle migrations
    Base.metadata.create_all(engine)

    oVariants = DBSession.query(Variant).filter_by(chrom=query_chrom,pos=query_position,ref=query_ref,alt=query_alt)
    oAnalysis = DBSession.query(Analysis)
    oSamples = DBSession.query(Sample).order_by(Sample.name)
    oAnalysis_Variants = DBSession.query(AnalysisVariant)





    insp = inspect(engine)
    meta = MetaData()




    for entry in analyses:
        print (entry.sample_id)


if __name__ == '__main__':
    main()
