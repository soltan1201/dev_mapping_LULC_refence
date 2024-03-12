import dict_statisticas_S2 as dict_stat
import numpy as np


lst_bnd = [
        "blue_median_wet","green_median_wet","red_median_wet",
        "nir_median_wet","swir1_median_wet","swir2_median_wet",
        "blue_median_dry","green_median_dry","red_median_dry",
        "nir_median_dry","swir1_median_dry","swir2_median_dry"  
    ];

dict_bnd= {
    "median_blue_median_wet": [],
    "median_green_median_wet": [],
    "median_red_median_wet": [],
    "median_nir_median_wet": [],
    "median_swir1_median_wet": [],
    "median_swir2_median_wet": [],
    "median_blue_median_dry": [],
    "median_green_median_dry": [],
    "median_red_median_dry": [],
    "median_nir_median_dry": [],
    "median_swir1_median_dry": [],
    "median_swir2_median_dry": [],
    "stdDev_blue_median_wet": [],
    "stdDev_green_median_wet": [],
    "stdDev_red_median_wet": [],
    "stdDev_nir_median_wet": [],
    "stdDev_swir1_median_wet": [],
    "stdDev_swir2_median_wet": [],
    "stdDev_blue_median_dry": [],
    "stdDev_green_median_dry": [],
    "stdDev_red_median_dry": [],
    "stdDev_nir_median_dry": [],
    "stdDev_swir1_median_dry": [],
    "stdDev_swir2_median_dry": []   
}

for kkey, dictStat in dict_stat.dictStat.items():
    print("loadindg images = " + kkey)
    for stat, dictbandVal in dictStat.items():
        print(f"       loading {stat} statistics ")
        for band, valor in dictbandVal.items():
            print(f"adding {band} => {valor}")
            lst_tmp = dict_bnd[stat + "_" + band]
            lst_tmp.append(valor)
            dict_bnd[stat + "_" + band] = lst_tmp


print(" \n ====== show mean and deviation values ========")
for band, lstVal in dict_bnd.items():
    print(f"show {band} = > {np.mean(lstVal)}")