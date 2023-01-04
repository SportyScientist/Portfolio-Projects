#Author: Marlene Ganslmeier

#Polars is not installed by default 
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


#file_path = input("Welcome. Please specify the path to your variant file here: ")
file_path = "chr1_2.gt.tsv.gz"

if file_path.endswith('.csv') or file_path.endswith('.csv.gz'):
    data = pl.read_csv(file_path, has_header = False)

elif file_path.endswith('.tsv') or file_path.endswith('.tsv.gz'):
    data = pl.read_csv(file_path, sep = "\t", has_header = False)

  
#get all chromosomes present
chr_pl = data.select(
    [
        pl.col("column_1").unique().alias("Chromosome")
    ]
)
# convert to seperated list for iteration later
chr_np = chr_pl.to_numpy()
chr_list = chr_np[:,0].tolist()

#initiate df for results
#result = pl.DataFrame({"Chr": [int], "Start": [int], "End": [int], "n_homs": [""]})
results = []
#we can't have stretches spanning chromosomes, therefore we go through each chromosome separate
#option would be to introduce a check if more than one chr is present, but don't think it makes a time difference?
for chr in chr_list:
    chr_data = data.filter(pl.col("column_1") == chr)
    chr_data = chr_data.sort("column_2")
        
    end = chr_data.shape[0] #get nrows

    #set to first row for now


    count = 0
    start = 0

    
    for locus in range(0,end):

        if pl.select(chr_data)[locus,"column_3"] == "1|1" or pl.select(chr_data)[locus,"column_3"] == "0|0":
            # print("jop")
            count +=1
        else:
            if count != 0:
                stretch = [chr, chr_data[start,1], chr_data[locus,1], count] # i was originally planning on concatenating polar series, but cs95 has a strong opinion against it https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-and-then-filling-it
                count = 0
                start = locus
                #print(stretch)
                #pl.concat([result, stretch], how="vertical")
                results.append(stretch)
            else:
                continue

df = pd.DataFrame(results, columns = ['Chr', 'Start', 'End', 'n_hom'])
print (df)
df.to_csv("results.csv")

time_2 = datetime.now()
difference = time_2 - time_1

print("This took:" + str(difference.total_seconds()) + "seconds")


       
       
       
       
         
            
