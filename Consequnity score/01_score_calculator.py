#Author: Marlene Ganslmeier

import sys
import os
import argparse
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

try:
    import pandas as pd
except ImportError:
    sys.exit("The python module pandas is required as a dependency. Please install the package with \'pip install -U polars\'")

parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="Location of file with loci", type=str)
parser.add_argument("--region_length", help="Length of homocygotic core region", type=int, default = 50)
parser.add_argument("--hom_score", help="positive float to weight homozygotic loci", type=float, default = 0.025)
parser.add_argument("--het_score", help="negative float to penalize heterozygotic loci", type=float, default = -0.975)
parser.add_argument("--depth", help="minimal sequencing depth of loci", type=int, default = 8)


args = parser.parse_args()

file_path = args.file_path
region_length = args.region_length

hom_score = args.hom_score
het_score = args.het_score
depth = args.depth


###############################################################
#read in file
###############################################################

if file_path.endswith('.csv') or file_path.endswith('.csv.gz'):
    data = pd.read_csv(file_path, header = 0)

elif file_path.endswith('.tsv') or file_path.endswith('.tsv.gz'):
    data = pd.read_csv(file_path, sep = "\t", header = 0)

data.columns = ["chr", "locus", "allele", "seq_depth"]

#unify data format
data['allele'] = data['allele'].str.replace('/','|')

#filter for autosomes only
ensemble = list(range(1,23))
uscs = ["chr"+str(i) for i in range(1, 23)]

chromosomes = ensemble + uscs
data = data[data['chr'].isin(chromosomes)]


#filter for sequencing depth
data = data.loc[data["seq_depth"] >= depth]

#get total number of homocygotic variants
hom_alleles = ["1|1", "0|0"]
total_hom_counts = data['allele'].isin(hom_alleles).sum()

#data = data[:10_000]

###############################################################
#define functions
###############################################################

def get_regions(chr_list):
     #initiate list for results
    results = []
    #we can't have stretches spanning chromosomes, therefore we go through each chromosome separate
    #option would be to introduce a check if more than one chr is present, but don't think it makes a time difference?
    for chr in chr_list:
        chr_data = data.loc[data["chr"] == chr]
        #print(chr_data)
            
        end = chr_data.shape[0] #get nrows

        #set to first row for now
        count = 0
        start = 0

        
        for item in range(0,end):

            if chr_data.iloc[item].loc["allele"] == "0|0" or chr_data.iloc[item].loc["allele"] == "1|1":
                count +=1
                
            else:
                if count != 0:
                    stretch = [chr, chr_data.iloc[start,1], chr_data.iloc[item,1], count] 
                    #print(stretch)
                    count = 0
                    start = item
                    results.append(stretch)
                else:
                    continue
        print("Chromosome ", chr, " done!")

    regions = pd.DataFrame(results, columns = ['chr', 'start', 'end', 'n_hom'])
    return regions


def get_score(data):
    data = data.assign(id = range(1, len(data) + 1))
    data['allele_score'] = data['allele'].apply(lambda x: hom_score if x in ["1|1","0|0"] else (het_score if x in ["1|0","0|1"] else x))
    data['allele_score'] = pd.to_numeric(data['allele_score'], errors='coerce')
    return data


def extend_regions():
    for chr in chr_list:
        
        chr_data = data.loc[data["chr"] == chr]

        chr_regions = regions_filt.loc[regions_filt["chr"] == chr]

        for reg in range(chr_regions.shape[0]):

            score = chr_regions.iloc[reg].loc["start_score"]
            start = chr_regions.iloc[reg].loc["start"]
            end = chr_regions.iloc[reg].loc["end"]
            n_hom = chr_regions.iloc[reg].loc["n_hom"]

            row_nr_start = chr_data.loc[chr_data['locus'] == start,'id'].iat[0]
            row_nr_end = chr_data.loc[chr_data['locus'] == end, 'id'].iat[0]
                
            n_het = 0

            while score > 0:
                row_nr_start += -1
                row_nr_end += 1
                start_score = chr_data.loc[chr_data['id'] == row_nr_start, 'allele_score'].iat[0]
                end_score = chr_data.loc[chr_data['id'] == row_nr_end, 'allele_score'].iat[0]


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
                        final_start = chr_data.loc[chr_data['id'] == row_nr_start +1, 'locus'].iat[0]
                    elif start_score >0 :
                        final_start = chr_data.loc[chr_data['id'] == row_nr_start, 'locus'].iat[0]

                    if end_score  <0 :
                        final_end = chr_data.loc[chr_data['id'] == row_nr_end -1, 'locus'].iat[0]
                    elif end_score >0 :
                        final_end = chr_data.loc[chr_data['id'] == row_nr_end, 'locus'].iat[0]

                    
                    len = int(final_end - final_start)
                    stretch = [chr, final_start, final_end, len, int(n_hom), n_het] 
                    results_extended.append(stretch)

    regions_extended = pd.DataFrame(results_extended, columns = ["chr", "start", "end", "len", "n_hom", "n_het"])
    return regions_extended

def get_chromosome_list(data):
    #get all chromosomes present
    chromosomes = data['chr'].unique()
    chr_list = chromosomes.tolist()
    return chr_list


###############################################################
#run functions
###############################################################
chr_list = get_chromosome_list(data)

regions = get_regions(chr_list)

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Regions are done. Current Time =", current_time)

regions_filt = regions[regions["n_hom"] > region_length]

regions_filt = regions_filt.assign(start_score=regions_filt["n_hom"] * hom_score)

regions_filt.to_csv("regions_filt.csv")

data = get_score(data)

results_extended = []
regions_extended = extend_regions()

total_region_length = regions_extended["len"].sum()

regions_extended["reg_score"] = regions_extended.apply(lambda x: round((total_region_length * x.n_hom) / total_hom_counts,2), axis=1)

#print(regions_extended)


for i in range(1,len(regions_extended)):
    if regions_extended.loc[i][1] < regions_extended.loc[i-1][2] and regions_extended.loc[i-1][0] == regions_extended.loc[i][0]:
        print("Overlap found!")

    

           
regions_extended.to_csv("results_extended.csv")


now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)



       
       
       
       
         
            