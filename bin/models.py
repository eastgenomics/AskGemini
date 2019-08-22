from base import Base

from sqlalchemy.orm import relationship
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
    func, or_,and_
)

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


class Transcript(Base):
    __tablename__ = "transcript"
    id = Column(Integer, primary_key = True)
    gene_id = Column(Integer,ForeignKey('gene.id'))
    refseq = Column(String(200))
    ens_id = Column(String(200))
    CCDS = Column(String(200))
    clinical_transcript = Column(Enum('Y','N'))
    comment = Column(String(200))

class SamplePanel(Base):
    __tablename__ =  "sample_panel"
    id = Column(Integer, primary_key = True)
    sample_id = Column(Integer,ForeignKey('sample.id'))
    panel_name = Column(String(200))