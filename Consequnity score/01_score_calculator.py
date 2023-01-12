#Author: Marlene Ganslmeier

import sys
import os
import argparse

try:
    import polars as pl
except ImportError:
    sys.exit("The python module Polars is required as a dependency. Please install the package with \'pip install -U polars\'")

parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="Location of file with loci", type=str)
parser.add_argument("--region_length", help="Length of homocygotic core region", type=int, default = 50)
parser.add_argument("--hom_score", help="positive float to weight homozygotic loci", type=float, default = 0.025)
parser.add_argument("--het_score", help="negative float to penalize heterozygotic loci", type=float, default = -0.975)

args = parser.parse_args()

file_path = args.file_path
region_length = args.region_length

hom_score = args.hom_score
het_score = args.het_score


###############################################################
#read in file
###############################################################

if file_path.endswith('.csv') or file_path.endswith('.csv.gz'):
    data = pl.read_csv(file_path, has_header = False)

elif file_path.endswith('.tsv') or file_path.endswith('.tsv.gz'):
    data = pl.read_csv(file_path, sep = "\t", has_header = False)

data.columns = ["chr", "locus", "allele", "seq_depth"]

###############################################################
#define functions
###############################################################

def get_regions(chr_list):
     #initiate list for results
    results = []
    #we can't have stretches spanning chromosomes, therefore we go through each chromosome separate
    #option would be to introduce a check if more than one chr is present, but don't think it makes a time difference?
    for chr in chr_list:
        chr_data = data.filter(pl.col("chr") == chr)
        chr_data = chr_data.sort("locus")
            
        end = chr_data.shape[0] #get nrows

        #set to first row for now
        count = 0
        start = 0

        
        for locus in range(0,end):

            if pl.select(chr_data)[locus,"allele"] == "1|1" or pl.select(chr_data)[locus,"allele"] == "0|0":
                count +=1
            else:
                if count != 0:
                    stretch = [chr, chr_data[start,1], chr_data[locus,1], count] # i was originally planning on concatenating polar series, but cs95 has a strong opinion against it https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-and-then-filling-it
                    count = 0
                    start = locus
                    results.append(stretch)
                else:
                    continue

    regions = pl.DataFrame(results, columns = ['chr', 'start', 'end', 'n_hom'])
    return regions

def get_score(data):
    data = data.with_row_count() # add rownumbers
    data = data.with_column( #add scores
        pl.when(pl.col("allele") == "1|1")
        .then(hom_score)
        .when(pl.col("allele") == "0|0")
        .then(hom_score)
        .when(pl.col("allele") == "1|0")
        .then(het_score)
        .when(pl.col("allele") == "0|1")
        .then(het_score)
        .otherwise(pl.col("allele")).alias("locus_score"),)
    data = data.with_column(pl.col("locus_score").cast(pl.Float64, strict=False))
    return data

def extend_regions():
    for chr in chr_list:
        
        chr_data = data.filter(pl.col("chr") == chr)  

        chr_regions = regions_filt.filter(pl.col("chr") == chr)

        for reg in range(chr_regions.shape[0]):

            score = pl.select(chr_regions)[reg,"start_score"]
            start = pl.select(chr_regions)[reg,"start"]
            end = pl.select(chr_regions)[reg,"end"]
            n_hom = pl.select(chr_regions)[reg,"n_hom"]

            row_nr_start = chr_data.filter(pl.col("locus") == start).select("row_nr")[0,0]   
            row_nr_end = chr_data.filter(pl.col("locus") == end).select("row_nr")[0,0]   
    
            n_het = 0

            while score > 0:
                row_nr_start += -1
                row_nr_end += 1
                start_score = chr_data.filter(pl.col("row_nr") == row_nr_start).select("locus_score")[0,0]
                end_score = chr_data.filter(pl.col("row_nr") == row_nr_end).select("locus_score")[0,0]

                if start_score <0 :
                    n_het += 1

                elif start_score >0 :
                    n_hom += 1
                        
                if end_score  <0 :
                    n_het += 1

                elif end_score >0 :     
                    n_hom += 1

                score += start_score
                score += end_score

                if score <0:
                    if start_score <0 :
                        final_start = chr_data.filter(pl.col("row_nr") == row_nr_start +1).select("locus")[0,0]
                        
                    elif start_score >0 :
                        final_start = chr_data.filter(pl.col("row_nr") == row_nr_start).select("locus")[0,0]

                    if end_score  <0 :
                        final_end = chr_data.filter(pl.col("row_nr") == row_nr_end -1).select("locus")[0,0]
                        
                    elif end_score >0 :
                        final_end = chr_data.filter(pl.col("row_nr") == row_nr_end).select("locus")[0,0]
                    
                    stretch = [chr, final_start, final_end, n_hom, n_het] 
                    results_extended.append(stretch)

    regions_extended = pl.DataFrame(results_extended, columns = ["chr", "start", "end", "n_hom", "n_het"])
    return regions_extended

def get_chromosome_list(data):
    #get all chromosomes present
    chr_pl = data.select(
        [
            pl.col("chr").unique().alias("chr")
        ]
    )
    # convert to seperated list for iteration later
    chr_np = chr_pl.to_numpy()
    chr_list = chr_np[:,0].tolist()
    return chr_list


###############################################################
#run functions
###############################################################
chr_list = get_chromosome_list(data)

if os.path.exists("results.csv") == False:

    print("Creating results.csv")
    regions = get_regions(chr_list)
    regions.write_csv("results.csv")
else:
    print("Reading in results")
    regions = pl.read_csv("results.csv")
   
regions_filt = regions.filter(pl.col("n_hom") >= region_length)

regions_filt = regions_filt.with_columns([
    (pl.col("n_hom") * hom_score).alias("start_score")])


data = get_score(data)

results_extended = []
regions_extended = extend_regions()
           
regions_extended.write_csv("results_extended.csv")






       
       
       
       
         
            