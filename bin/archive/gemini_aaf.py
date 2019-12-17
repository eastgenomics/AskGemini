#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (May 2019), contact: adriana.toutoudaki@addenbrookes.nhs.uk

from sqlalchemy import create_engine
import pandas
import argparse
import csv
import sys,os
from datetime import datetime



now = datetime.now()
#results_file = now.isoformat() + "_" + str(chrom)  + "_" + str(position) + "_" + ref + "_" + alt +".txt"


#password = input("Please enter the database password ")
password = 'readonly'
database_string = "mysql://ga_ro:readonly@sql01/genetics_ark_1_1_0"
engine = create_engine(database_string)

connection = engine.connect()

pre_stmt = "select sample.name, analysis_variant.depth, analysis_variant.quality , analysis_variant.AAF, analysis_variant.allele_count from analysis join sample on sample.id = analysis.sample_id join analysis_variant on analysis.id = analysis_variant.analysis_id join variant on variant.id = analysis_variant.variant_id "
where_stmt = "where (variant.chrom = {0} and variant.pos = {1} and variant.ref = '{2}' and variant.alt = '{3}') order by sample.name;".format(chrom,position,ref,alt)
stmt = pre_stmt + where_stmt

result = connection.execute(stmt).fetchall()

#meta = MetaData(engine, reflect=True)

rd = []
allele_count = 0
for row in result:
    query = str(row).strip("()',")
    x = query.split(',')

    parsed_row = [x[0].strip("'"),x[1].strip(),x[2].strip(),x[3].strip(),x[4].strip()]
    rd.append(parsed_row)

sample_query = connection.execute("select count(*) from sample where sample.project_id = 1 or sample.project_id =2")

for row in sample_query:
    sample_sum = int(str(row).strip('(),'))

connection.close()


results_file = str((now.isoformat()[:10])) + "_" + str(chrom)  + "_" + str(position)+  "_" + ref + "_" + alt +".txt"



with open(results_file, "+w") as sample_file:
    sample_writer = csv.writer(sample_file,delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    sample_writer.writerow(['Sample','Depth','Qual','AAF','Allele_Count'])
    
    for v, entry in enumerate(rd):
        sample_writer.writerow(rd[v])

        allele_count += int(rd[v][4])


    freq = allele_count / (sample_sum*2)

    sample_writer.writerow(['Gemini','Frequency', freq])

print ("The frequency of the requested variant is :", round(freq,5))
print ('\n *** A .txt file containing the list of samples has been successfully created. ***')
print ("Filename: ", results_file)

