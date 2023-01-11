import polars as pl
import plotly.express as px

#variables
file = "results.csv"

region_length = 50
hom_score = 0.025

regions = pl.read_csv(file, has_header = True)
regions_filt = regions.filter(pl.col("n_hom") >= region_length)

regions_filt = regions_filt.with_columns([
    (pl.col("n_hom") * hom_score).alias("start_score")
])

#fig = px.histogram(regions.to_pandas(), x = "n_hom")
#fig.write_image("region_hist.png") #for some reason this stalls on my PC but I suscpect it to be the installation #windows


data = pl.read_csv("chr1_2.gt.tsv.gz", sep = "\t", has_header = False)

chr_pl = data.select(
    [
        pl.col("column_1").unique().alias("Chromosome")
    ]
)
# convert to seperated list for iteration later
chr_np = chr_pl.to_numpy()
chr_list = chr_np[:,0].tolist()

data = data.with_row_count() # add rownumbers
data = data.with_column( #add scores
    pl.when(pl.col("column_3") == "1|1")
    .then(0.025)
    .when(pl.col("column_3") == "0|0")
    .then(0.025)
    .when(pl.col("column_3") == "1|0")
    .then(-0.975)
    .when(pl.col("column_3") == "0|1")
    .then(-0.975)
    .otherwise(pl.col("column_3")).alias("locus_score"),
)

data = data.with_column(pl.col("locus_score").cast(pl.Float64, strict=False))
results_extended = []

for chr in chr_list:
    
    chr_data = data.filter(pl.col("column_1") == chr)
    chr_data = chr_data.sort("column_2")

    chr_regions = regions_filt.filter(pl.col("Chr") == chr)
    #print(chr_regions)

    for reg in range(chr_regions.shape[0]):

        score = pl.select(regions_filt)[reg,"start_score"]
        start = pl.select(regions_filt)[reg,"Start"]
        end = pl.select(regions_filt)[reg,"End"]
        n_hom = pl.select(regions_filt)[reg,"n_hom"]

        row_nr_start = chr_data.filter(pl.col("column_2") == start).select("row_nr")[0,0]   
        row_nr_end = chr_data.filter(pl.col("column_2") == end).select("row_nr")[0,0]    

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

                    final_start = pl.select(chr_data)[(row_nr_start + 1),"column_2"]
                    
                elif pl.select(chr_data)[(row_nr_start),"locus_score"] >0 :

                    final_start = pl.select(chr_data)[(row_nr_start),"column_2"]

                if pl.select(chr_data)[(row_nr_end),"locus_score"]  <0 :

                    final_end = pl.select(chr_data)[(row_nr_end - 1),"column_2"]
                    
                elif pl.select(chr_data)[(row_nr_end),"locus_score"] >0 :

                    final_end = pl.select(chr_data)[(row_nr_end),"column_2"]
                
                stretch = [chr, final_start, final_end, n_hom, n_het] 
                results_extended.append(stretch)

                print(stretch)


            
        