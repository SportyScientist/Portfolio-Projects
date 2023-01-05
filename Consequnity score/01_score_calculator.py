#Author: Marlene Ganslmeier

import sys
from datetime import datetime

time_1 = datetime.now()

try:
    import polars as pl
except ImportError:
    sys.exit("The python module Polars is required as a dependency. Please install the package with \'pip install -U polars\'")

try:
    import numpy as np
except ImportError:
    sys.exit("The python module NumPy is required as a dependency. Please install the package with \'pip install numpy\'")

try:
    import pandas as pd
except ImportError:
    sys.exit("The python module NumPy is required as a dependency. Please install the package with \'pip install pandas\'")


#variables
region_length = 50
hom_score = 0.025
het_score = -0.975


#file_path = input("Welcome. Please specify the path to your variant file here: ")
file_path = "chr1_2.gt.tsv.gz"

if file_path.endswith('.csv') or file_path.endswith('.csv.gz'):
    data = pl.read_csv(file_path, has_header = False)

elif file_path.endswith('.tsv') or file_path.endswith('.tsv.gz'):
    data = pl.read_csv(file_path, sep = "\t", has_header = False)

data.columns = ["chr", "locus", "allele", "seq_depth"]

#get all chromosomes present
chr_pl = data.select(
    [
        pl.col("chr").unique().alias("chr")
    ]
)
# convert to seperated list for iteration later
chr_np = chr_pl.to_numpy()
chr_list = chr_np[:,0].tolist()

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

regions = pd.DataFrame(results, columns = ['chr', 'start', 'end', 'n_hom'])
regions.to_csv("results.csv")

regions = pl.from_pandas(regions)
regions_filt = regions.filter(pl.col("n_hom") >= region_length)

regions_filt = regions_filt.with_columns([
    (pl.col("n_hom") * hom_score).alias("start_score")
])

#fig = px.histogram(regions.to_pandas(), x = "n_hom")
#fig.write_image("region_hist.png") #for some reason this stalls on my PC but I suscpect it to be the installation #windows


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
    .otherwise(pl.col("allele")).alias("locus_score"),
)

data = data.with_column(pl.col("locus_score").cast(pl.Float64, strict=False))
results_extended = []

for chr in chr_list:
    
    chr_data = data.filter(pl.col("chr") == chr)
    chr_data = chr_data.sort("chr")

    chr_regions = regions_filt.filter(pl.col("chr") == chr)
    #print(chr_regions)

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

            if pl.select(chr_data)[(row_nr_start),"locus_score"] <0 :
                    
                n_het += 1

            elif pl.select(chr_data)[(row_nr_start),"locus_score"] >0 :

                n_hom += 1
                    

            if pl.select(chr_data)[(row_nr_end),"locus_score"]  <0 :

                n_het += 1

            elif pl.select(chr_data)[(row_nr_end),"locus_score"] >0 :
                
                n_hom += 1


            score += pl.select(chr_data)[(row_nr_start),"locus_score"]
            score += pl.select(chr_data)[(row_nr_end),"locus_score"]

            #print(score)
            if score <0:
                if pl.select(chr_data)[(row_nr_start),"locus_score"] <0 :

                    final_start = pl.select(chr_data)[(row_nr_start + 1),"locus"]
                    
                elif pl.select(chr_data)[(row_nr_start),"locus_score"] >0 :

                    final_start = pl.select(chr_data)[(row_nr_start),"locus"]

                if pl.select(chr_data)[(row_nr_end),"locus_score"]  <0 :

                    final_end = pl.select(chr_data)[(row_nr_end - 1),"locus"]
                    
                elif pl.select(chr_data)[(row_nr_end),"locus_score"] >0 :

                    final_end = pl.select(chr_data)[(row_nr_end),"locus"]
                
                stretch = [chr, final_start, final_end, n_hom, n_het] 
                results_extended.append(stretch)

                print(stretch)


            
        

regions_extended = pd.DataFrame(results_extended, columns = ["chr", "start", "end", "n_hom", "n_het"])
regions_extended.to_csv("results_extended.csv")


time_2 = datetime.now()
difference = time_2 - time_1

print("This took:" + str(difference.total_seconds()) + "seconds")




       
       
       
       
         
            
