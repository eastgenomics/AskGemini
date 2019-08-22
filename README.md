# STP_programming

A program developed as part of the Programming module for the Scientist Training Programme (August 2019).

Main objective of this project is to create a useful python tool for interrogating the Gemini Database.

Modules required if not already installed(version used during development): 
*  Zope==4.1.1 (specifically zope.sqlalchemy==1.1)
*  SQLAlchemy==1.3.7
*  mysqlclient==1.3.10 (installed using conda)

    
### Tool usage: 

```bash 
    extract.py [-h] {calculate_geminiAF,get_genes, get_panels} 

    
    Extract information from GeminiDB
    

    positional arguments:
    {calculate_geminiAF,get_genes,get_panels}
    
    calculate_geminiAF  Given a chromosomal position and ref and alt
                        calculates the frequency in GeminiDB
        
        usage: extract.py calculate_geminiAF [-h] Chrom Pos Ref Alt

        positional arguments:
          Chrom       Enter the variant chromosome
          Pos         Enter the variant position
          Ref         Enter the reference allele
          Alt         Enter the alternative allele

    get_genes           Extracts all genes present in requested panel
        
        usage: extract.py get_genes [-h] [-t] [-s] panel

        positional arguments:
        panel       Enter Panel name

        optional arguments:
          -h, --help  show this help message and exit
          -t          Returns Gene names with clinically active transcripts
          -s          Returns all sample for a panel

    get_panels          Extracts all panels a requested gene is present.
        
        usage: extract.py get_panels [-h] gene

    positional arguments:
    gene        Enter Gene name


    optional arguments:
      -h, --help            show this help message and exit

   
```
