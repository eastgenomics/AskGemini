# STP_programming

A program developed as part of the Programming module for the Scientist Training Programme.

Main objective of this project is to create a useful python tool for interrogating the Gemini Database.

Initial requirements include(collected on the 5/08/19):
* calculate geminig AAF for a specific SNP  
    * export a list of samples containining that SNP
*  export all variants for a specific gene  
* extract panel information:
    * every gene in a panel
    * every panel that a gene is in 
    * every sample for a panel
* extract transcript information
    * which transcript is active
    * variants for a specific transcript
    
###Tool usage: 
 
 `extractor.py [-h] {calculate_geminiAF,get_panel_genes} `...

    
    Extract information from GeminiDB

    positional arguments:
    {calculate_geminiAF,get_panel_genes}
                        
    
    calculate_geminiAF  Given a chromosomal position and ref and alt
                        calculates the frequency in GeminiDB
                        
                         extractor.py calculate_geminiAF [-h] Chrom Pos Ref Alt

                        positional arguments:
                          Chrom       Enter the variant chromosome
                          Pos         Enter the variant position
                          Ref         Enter the reference allele
                          Alt         Enter the alternative allele

    
    get_panel_genes     Extracts all genes present in requested panel
                        usage: extractor.py get_panel_genes [-h] [--panel PANEL] [-t] [-s]
                                    [--gene GENE]

                        optional arguments:
                          --panel PANEL  Enter Panel name
                          -t             Returns gene names with clinically active transcripts
                          -s             Returns all samples for a panel
                          --gene GENE    Given a gene name, returns all panels that gene is in


    optional arguments:
        -h, --help            show this help message and exit

