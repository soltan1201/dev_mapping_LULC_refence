#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""

import ee
import gee
import json
import copy
import csv
import sys
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


class ClassMosaic_indexs_Spectral(object):

    feat_pts_true = ee.FeatureCollection([])
    lst_bnd = [
        "blue_median_wet","green_median_wet","red_median_wet",
        "nir_median_wet","swir1_median_wet","swir2_median_wet",
        "blue_median_dry","green_median_dry","red_median_dry",
        "nir_median_dry","swir1_median_dry","swir2_median_dry" 
    ]
    dict_stat_bnd= {
        "median_blue_median_wet": 1096.0578160344407,
        "median_green_median_wet": 1098.709489027003,
        "median_red_median_wet": 976.5168696816625,
        "median_nir_median_wet": 2488.803981135233,
        "median_swir1_median_wet": 2590.708057737918,
        "median_swir2_median_wet": 1491.7623228609739,
        "median_blue_median_dry": 1172.7243955891456,
        "median_green_median_dry": 1169.1687031130916,
        "median_red_median_dry": 1279.6717378018277,
        "median_nir_median_dry": 2019.8880081974671,
        "median_swir1_median_dry": 3143.650563677744,
        "median_swir2_median_dry": 2093.1297194020954,
        "stdDev_blue_median_wet": 216.81962108751355,
        "stdDev_green_median_wet": 259.92685500367475,
        "stdDev_red_median_wet": 375.5613485310523,
        "stdDev_nir_median_wet": 438.60626940637314,
        "stdDev_swir1_median_wet": 513.3187279778745,
        "stdDev_swir2_median_wet": 466.0627768106192,
        "stdDev_blue_median_dry": 142.54110653132767,
        "stdDev_green_median_dry": 215.4591413723328,
        "stdDev_red_median_dry": 346.9520939981621,
        "stdDev_nir_median_dry": 451.598842719077,
        "stdDev_swir1_median_dry": 577.197374855401,
        "stdDev_swir2_median_dry": 498.71129520994134   
    }
    # default options
    options = {
        'bioma': 'CAATINGA',
        'asset_mapbiomasCol8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
        'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
        'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
        'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
        'inAssetROIsPolg': 'projects/mapbiomas-arida/coletaMapaRef',
        'outAssetROIs': 'projects/mapbiomas-arida/coletaMapaRef',
        'nom_vector_coleta': 'amostras_coletadas_mapa_referencia_2022_S2_v3A',
        # projects/mapbiomas-arida/coletaMapaRef/amostras_coletadas_mapa_referencia_2022_S2_v3
        'carta_selected': "SC-24-V-D",
        'subgrade': 0,
        'lsClasse': [3, 4, 12, 15, 18, 21, 22, 33, 29],
        'lsPtos': [3000, 2000, 3000, 1500, 1500, 1000, 1500, 1000, 1000],
        "anoIntInit": 1985,
        "anoIntFin": 2022,
        'janela': 3
    }

    def __init__(self, myGeom, nyear, myClassify):

        self.regionInterest = ee.Geometry(myGeom)

        imgColGeodatin = ee.ImageCollection(self.options['asset_geodatin_next']).merge(
                            ee.ImageCollection(self.options['asset_geodatin_work'])).filter(
                                ee.Filter.eq('year', nyear)).filterBounds(self.regionInterest);
        
        self.imgMosaic = imgColGeodatin.map(lambda img: self.process_normalized_img(img))
                                                    
        # print("  ", self.imgMosaic.size().getInfo())
        print("see band Names of the first imagem")
        print("     " ,ee.Image(self.imgMosaic.first()).bandNames().getInfo())
        self.imgMosaic = self.imgMosaic.median()
        self.myClassify = myClassify
        

    def process_normalized_img (self, imgA):
        imgNorm = imgA.select(["blue_median_wet"]).lt(-1).rename("constant");
        for bnd in self.lst_bnd:
            medianBnd = self.dict_stat_bnd["median_" + bnd]
            stdDevBnd = self.dict_stat_bnd["stdDev_" + bnd];
            
            #  calcZ = (arrX - xmean) / xstd;
            calcZ = imgA.select(bnd).subtract(ee.Image.constant(medianBnd)) \
                                .divide(ee.Image.constant(stdDevBnd));
            #  expBandAft =  np.exp(-1 * calcZ)
            expBandAft = calcZ.multiply(ee.Image.constant(-1)).exp();
            #   return 1 / (1 + expBandAft)
            bndend = expBandAft.add(ee.Image.constant(1)).pow(ee.Image.constant(-1));

            imgNorm = imgNorm.addBands(bndend.rename(bnd));
        
        return imgNorm.toFloat().select(self.lst_bnd)

    
    #endregion


    
    
    def exportar_spectral_values_fromMosaic(self):

        # colecao responsavel por executar o controle de execucao, caso optem 
        # por executar o codigo em terminais paralelos,
        # ou seja, em mais de um terminal simultaneamente..
        # caso deseje executar num unico terminal, deixar colecao vazia.        
        # colecaoPontos = ee.FeatureCollection([])
        # lsNoPtos = []

        
        nameFeatROIs = self.options['nom_vector_coleta'] 
        if self.myClassify == 'gradient_tree_boost':
            nameFeatROIs = nameFeatROIs.replace('_coletadas_', '_ptos_samples_')

        print("path" , self.options['inAssetROIsPolg'] + '/' + nameFeatROIs)
        featROIsPol = ee.FeatureCollection(self.options['inAssetROIsPolg'] + '/' + nameFeatROIs)
        print("numero de poligons: ", featROIsPol.size().getInfo())  

        img_recMosaicnewB = self.CalculateIndice(self.imgMosaic)
        print("coletando todos os indexs ")
        bndAdd = img_recMosaicnewB.bandNames().getInfo()
        print(f"know bands names {len(bndAdd)}")

        # print("numero de ptos controle ", roisAct.size().getInfo())
        # opcoes para o sorteio estratificadoBuffBacia
        # featROIsPol
        ptosTemp = img_recMosaicnewB.sampleRegions(
                            collection= featROIsPol,
                            properties= ['classe'],
                            scale= 10,
                            tileScale= 1,
                            geometries= True
                        )
        # insere informacoes em cada ft
        ptosTemp = ptosTemp.filter(ee.Filter.notNull(['red_median_wet']))
        # merge com colecoes anteriores
        # colecaoPontos = colecaoPontos.merge(ptosTemp)            
        # sys.exit()
        name_exp = nameFeatROIs + "_points"  
        self.save_ROIs_toAsset(ee.FeatureCollection(ptosTemp), name_exp)        
    
    # salva ftcol para um assetindexIni
    def save_ROIs_toAsset(self, collection, name):

        optExp = {
            'collection': collection,
            'description': name,
            'assetId': self.options['outAssetROIs'] + "/" + name
        }

        task = ee.batch.Export.table.toAsset(**optExp)
        task.start()
        print("exportando ROIs da bacia $s ...!", name)


param = {
    'bioma': ["CAATINGA", 'CERRADO', 'MATAATLANTICA'],
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'carta_selected': "SC-24-V-D",
    'subgrade': 0,
    'sufix': "_1",
    'numeroTask': 6,
    'numeroLimit': 40,
    'conta': {
        '0': 'caatinga01',
        '6': 'caatinga02',
        '12': 'caatinga03',
        '18': 'caatinga04',
        '24': 'caatinga05',
        '30': 'solkan1201',
        '36': 'diegoGmail',
        # '20': 'rodrigo'
    },
}
def gerenciador(cont, param):

    numberofChange = [kk for kk in param['conta'].keys()]

    if str(cont) in numberofChange:

        gee.switch_user(param['conta'][str(cont)])
        gee.init()
        gee.tasks(n=param['numeroTask'], return_list=True)

    elif cont > param['numeroLimit']:
        cont = 0

    cont += 1
    return cont


year_select = 2020
regiaoCaat = ee.FeatureCollection(param['subGridsAsset']).filter(
                    ee.Filter.eq("grid", param['carta_selected'])).filter(
                          ee.Filter.eq("subgrid_id", param['subgrade'])) \
                        .geometry();

# cont = gerenciador(0, param)
# 'random_forest'
# 'gradient_tree_boost'
# 'support_vector_machine':
oClassificador = 'gradient_tree_boost'
objetoMosaic_exportROI = ClassMosaic_indexs_Spectral(regiaoCaat, year_select, oClassificador)
# geobacia, colAnos, nomeBacia, dict_nameBN4
objetoMosaic_exportROI.exportar_spectral_values_fromMosaic()
# cont = gerenciador(cont, param)
