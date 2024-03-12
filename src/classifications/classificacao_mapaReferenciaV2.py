#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import gee
import json
import csv
import copy
import sys
import math
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
# sys.setrecursionlimit(1000000000)

#============================================================


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
        'asset_gedi': 'users/potapovpeter/GEDI_V27',
        'asset_geodatin_urbano': 'projects/mapbiomas-arida/coletaMapaRef/mascara_area_urbana_image',
        'asset_geodatin_agro': 'projects/mapbiomas-arida/coletaMapaRef/mascara_area_agricultura_image',
        'asset_geodatin_campo': 'projects/mapbiomas-arida/coletaMapaRef/mascara_areas_campestre_image',
        'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
        'inAssetROIsPolg': 'projects/mapbiomas-arida/coletaMapaRef',
        'outAssetROIs': 'projects/mapbiomas-arida/coletaMapaRef',
        'output_class': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias',
        'nom_vector_coletav2': 'amostras_coletadas_mapa_referencia_2022_S2_v2_points',
        'nom_vector_coletav3': 'amostras_coletadas_mapa_referencia_2022_S2_v3A_points',
        'nom_ROIs_coletaCampo': 'poligons_area_campestre_points',
        'carta_selected': "SC-24-V-D",
        'subgrade': 0,
        'lsClasse': [3, 4, 12, 15, 18, 21, 22, 33, 29],
        'lsPtos': [3000, 2000, 3000, 1500, 1500, 1000, 1500, 1000, 1000],
        'version': '51',
        'janela': 3,
        'pmtRF': {
            'numberOfTrees': 365, 
            'variablesPerSplit': 15,
            'minLeafPopulation': 40,
            'bagFraction': 0.8,
            'seed': 0
        }, 
        # https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
        'pmtGTB': {
            'numberOfTrees': 45, 
            'shrinkage': 0.1,         
            'samplingRate': 0.75,            
            'loss': "LeastAbsoluteDeviation",#'Huber',#'LeastAbsoluteDeviation', LeastSquares
            'seed': 0
        },
        'pmtSVM' : {
            'decisionProcedure' : 'Margin', 
            'kernelType' : 'RBF', 
            'shrinking' : True, 
            'gamma' : 0.001
        },
        'dictClassModel':{
            'random_forest': 'RF',
            'gradient_tree_boost': 'GTB',
            'support_vector_machine': 'SVM'
        } 

    }
    # versão 1 de pontos {'15': 33968, '18': 57820, '24': 12100, '25': 7803, '29': 5804, '33': 29591, '4': 49515}
    bandas_imports = [
        'blue_median_wet', 'green_median_wet', 'red_median_wet', 'nir_median_wet', 'swir1_median_wet', 
        'swir2_median_wet', 'blue_median_dry', 'green_median_dry', 'red_median_dry', 'nir_median_dry', 
        'swir1_median_dry', 'swir2_median_dry', 'evi_median_wet', 'evi_median_dry', 'ratio_median_wet', 
        'ratio_median_dry', 'rvi_median_wet', 'rvi_median', 'ndwi_median_wet', 'ndwi_median_dry', 
        'gvmi_median_wet', 'gvmi_median_dry', 'awei_median_wet', 'awei_median_dry', 'iia_median_wet', 
        'iia_median_dry', 'gcvi_median_wet', 'gcvi_median_dry', 'gemi_median_wet', 'gemi_median_dry', 
        'cvi_median_wet', 'cvi_median_dry', 'gli_median_wet', 'gli_median_dry', 'shape_median_wet', 
        'shape_median_dry', 'afvi_median_wet', 'afvi_median_dry', 'avi_median_wet', 'avi_median_dry', 
        'bsi_median_wet', 'bsi_median_dry', 'brba_median_wet', 'brba_median_dry', 'dswi5_median_wet', 
        'dswi5_median_dry', 'lswi_median_wet', 'lswi_median_dry', 'mbi_median_wet', 'mbi_median_dry', 
        'ui_median_wet', 'ui_median_dry', 'ri_median_wet', 'ri_median_dry', 'osavi_median_wet', 
        'osavi_median_dry', 'wetness_median_wet', 'wetness_median_dry', 'brightness_median_wet', 
        'brightness_median_dry', 'nir_median_wet_contrast', 'red_median_wet_contrast', 
        'nir_median_dry_contrast', 'red_median_dry_contrast'
    ]
    
    bandas_selected = [
        'awei_median_dry','awei_median_wet', 'brba_median_dry', 'brba_median_wet',
        'gemi_median_dry', 'gemi_median_wet', 'wetness_median_wet', 'wetness_median_dry',
        'brightness_median_dry', 'brightness_median_wet', 'ratio_median_dry', 'ratio_median_wet', 
        'shape_median_dry', 'shape_median_wet', 'cvi_median_dry', 'cvi_median_wet',
        'dswi5_median_dry', 'dswi5_median_wet', 'rvi_median_wet', 'swir1_median_dry',
        'gcvi_median_dry', 'gcvi_median_wet', 'evi_median_dry', 'evi_median_wet',
        'blue_median_dry', 'blue_median_wet', 'green_median_wet', 'gvmi_median_dry',
        'swir2_median_dry', 'swir2_median_wet', 'red_median_dry_contrast', 'red_median_wet_contrast', 
        'ui_median_dry', 'ui_median_wet', 'ri_median_dry', 'ri_median_wet',  
        'osavi_median_dry', 'osavi_median_wet', 'ndwi_median_dry', 'ndwi_median_wet',
        'afvi_median_dry', 'afvi_median_wet'  
    ]   

    bandas_selected_GBT = [
        'awei_median_dry', 'awei_median_wet', 'brba_median_dry', 'brba_median_wet', 
        'gemi_median_dry', 'gemi_median_wet', 'wetness_median_wet', 'wetness_median_dry', 
        'brightness_median_dry', 'brightness_median_wet', 'ratio_median_dry', 
        'ratio_median_wet', 'shape_median_dry', 'shape_median_wet', 'cvi_median_dry', 
        'cvi_median_wet', 'dswi5_median_dry', 'dswi5_median_wet', 'rvi_median_wet', 
        'gcvi_median_dry', 'gcvi_median_wet', 'evi_median_dry', 'evi_median_wet', 
        # 'blue_median_dry', 'blue_median_wet', 'green_median_wet', 
        'gvmi_median_dry', 
        # 'swir2_median_dry', 'swir2_median_wet'
    ]

    def __init__(self, myGeom, nyear, nclassificador, subGrade):

        self.regionInterest = ee.Geometry(myGeom)
        self.options['subgrade'] = subGrade
        imgColGeodatin = ee.ImageCollection(self.options['asset_geodatin_next']).merge(
                            ee.ImageCollection(self.options['asset_geodatin_work'])).filter(
                                ee.Filter.eq('year', nyear)).filterBounds(self.regionInterest);
        
        self.imgMosaic = imgColGeodatin.map(lambda img: self.process_normalized_img(img))
                                                    
        # print("  ", self.imgMosaic.size().getInfo())
        print("see band Names of the first imagem")
        print("     " ,ee.Image(self.imgMosaic.first()).bandNames().getInfo())
        self.imgMosaic = self.imgMosaic.median()
        ## ======== classificador ===============
        self.classificador = nclassificador # 'random_forest'
        ## ======== bandas classificador ===============
        if nclassificador == 'gradient_tree_boost':
            self.bandas_selected = copy.deepcopy(self.bandas_selected_GBT)
        

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

    #region Bloco de functions de calculos de Indices 
    # Ratio Vegetation Index
    def agregateBandsIndexRATIO(self, img):
        print("processing agregateBandsIndexRATIO")
        ratioImgwet = img.expression("float(b('nir_median_wet') / b('red_median_wet'))")\
                                .rename(['ratio_median_wet']).toFloat()  

        ratioImgdry = img.expression("float(b('nir_median_dry') / b('red_median_dry'))")\
                                .rename(['ratio_median_dry']).toFloat()        

        return img.addBands(ratioImgwet).addBands(ratioImgdry)

    # Ratio Vegetation Index
    def agregateBandsIndexRVI(self, img):
        print("processing agregateBandsIndexRVI")
        rviImgWet = img.expression("float(b('red_median_wet') / b('nir_median_wet'))")\
                                .rename(['rvi_median_wet']).toFloat() 

        rviImgDry = img.expression("float(b('red_median_dry') / b('nir_median_dry'))")\
                                .rename(['rvi_median']).toFloat()       

        return img.addBands(rviImgWet).addBands(rviImgDry)
    
    def agregateBandsIndexNDVI(self, img):
        print("processing agregateBandsIndexNDVI")  
        ndviImgWet = img.expression("float(b('nir_median_wet') - b('red_median_wet')) / (b('nir_median_wet') + b('red_median_wet'))")\
                                .rename(['ndvi_median_wet']).toFloat()  

        ndviImgDry = img.expression("float(b('nir_median_dry') - b('red_median_dry')) / (b('nir_median_dry') + b('red_median_dry'))")\
                                .rename(['ndvi_median_dry']).toFloat()     

        return img.addBands(ndviImgWet).addBands(ndviImgDry)

    def agregateBandsIndexWater(self, img):
        print("processing agregateBandsIndexWater")  
        ndwiImgWet = img.expression("float(b('nir_median_wet') - b('swir2_median_wet')) / (b('nir_median_wet') + b('swir2_median_wet'))")\
                                .rename(['ndwi_median_wet']).toFloat()   

        ndwiImgDry = img.expression("float(b('nir_median_dry') - b('swir2_median_dry')) / (b('nir_median_dry') + b('swir2_median_dry'))")\
                                .rename(['ndwi_median_dry']).toFloat()   

        return img.addBands(ndwiImgWet).addBands(ndwiImgDry)
    
    def AutomatedWaterExtractionIndex(self, img): 
        print("processing AutomatedWaterExtractionIndex")   
        aweiWet = img.expression(
                            "float(4 * (b('green_median_wet') - b('swir2_median_wet')) - (0.25 * b('nir_median_wet') + 2.75 * b('swir1_median_wet')))"
                        ).rename("awei_median_wet").toFloat() 

        aweiDry = img.expression(
                            "float(4 * (b('green_median_dry') - b('swir2_median_dry')) - (0.25 * b('nir_median_dry') + 2.75 * b('swir1_median_dry')))"
                        ).rename("awei_median_dry").toFloat()          
        
        return img.addBands(aweiWet).addBands(aweiDry)
    
    def IndiceIndicadorAgua(self, img):   
        print("processing IndiceIndicadorAgua") 
        iiaImgWet = img.expression(
                            "float((b('green_median_wet') - 4 *  b('nir_median_wet')) / (b('green_median_wet') + 4 *  b('nir_median_wet')))"
                        ).rename("iia_median_wet").toFloat()

        iiaImgDry = img.expression(
                            "float((b('green_median_dry') - 4 *  b('nir_median_dry')) / (b('green_median_dry') + 4 *  b('nir_median_dry')))"
                        ).rename("iia_median_dry").toFloat()
        
        return img.addBands(iiaImgWet).addBands(iiaImgDry)
    
    def agregateBandsIndexEVI(self, img):
        print("processing agregateBandsIndexEVI")
        eviImgWet = img.expression(
            "float(2.4 * (b('nir_median_wet') - b('red_median_wet')) / (1 + b('nir_median_wet') + b('red_median_wet')))")\
                .rename(['evi_median_wet'])   

        eviImgDry = img.expression(
            "float(2.4 * (b('nir_median_dry') - b('red_median_dry')) / (1 + b('nir_median_dry') + b('red_median_dry')))")\
                .rename(['evi_median_dry'])   
        
        return img.addBands(eviImgWet).addBands(eviImgDry)

    def agregateBandsIndexGVMI(self, img):
        print("processing agregateBandsIndexGVMI")
        gvmiImgWet = img.expression(
                        "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) / ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                    ).rename(['gvmi_median_wet']).toFloat()

        gvmiImgDry = img.expression(
                        "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) / ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                    ).rename(['gvmi_median_dry']).toFloat()  
    
        return img.addBands(gvmiImgWet).addBands(gvmiImgDry)
    
    def agregateBandsIndexLAI(self, img):
        print("processing agregateBandsIndexLAI")
        laiImgY = img.expression(
            "float(3.618 * (b('evi_median') - 0.118))")\
                .rename(['lai_median']).toFloat()
    
        return img.addBands(laiImgY)    

    def agregateBandsIndexGCVI(self, img):    
        print("processing agregateBandsIndexGCVI")
        gcviImgAWet = img.expression(
            "float(b('nir_median_wet')) / (b('green_median_wet')) - 1")\
                .rename(['gcvi_median_wet']).toFloat() 
                
        gcviImgADry = img.expression(
            "float(b('nir_median_dry')) / (b('green_median_dry')) - 1")\
                .rename(['gcvi_median_dry']).toFloat()      
        
        return img.addBands(gcviImgAWet).addBands(gcviImgADry)

    # Global Environment Monitoring Index GEMI 
    def agregateBandsIndexGEMI(self, img):    
        print("processing agregateBandsIndexGEMI")
        # "( 2 * ( NIR ^2 - RED ^2) + 1.5 * NIR + 0.5 * RED ) / ( NIR + RED + 0.5 )"
        gemiImgAWet = img.expression(
            "float((2 * (b('nir_median_wet') * b('nir_median_wet') - b('red_median_wet') * b('red_median_wet')) + 1.5 * b('nir_median_wet')" +
            " + 0.5 * b('red_median_wet')) / (b('nir_median_wet') + b('green_median_wet') + 0.5) )")\
                .rename(['gemi_median_wet']).toFloat() 

        gemiImgADry = img.expression(
            "float((2 * (b('nir_median_dry') * b('nir_median_dry') - b('red_median_dry') * b('red_median_dry')) + 1.5 * b('nir_median_dry')" +
            " + 0.5 * b('red_median_dry')) / (b('nir_median_dry') + b('green_median_dry') + 0.5) )")\
                .rename(['gemi_median_dry']).toFloat()     
        
        return img.addBands(gemiImgAWet).addBands(gemiImgADry)

    # Chlorophyll vegetation index CVI
    def agregateBandsIndexCVI(self, img): 
        print("processing agregateBandsIndexCVI")   
        cviImgAWet = img.expression(
            "float(b('nir_median_wet') * (b('green_median_wet') / (b('blue_median_wet') * b('blue_median_wet'))))")\
                .rename(['cvi_median_wet']).toFloat()

        cviImgADry = img.expression(
            "float(b('nir_median_dry') * (b('green_median_dry') / (b('blue_median_dry') * b('blue_median_dry'))))")\
                .rename(['cvi_median_dry']).toFloat()      
        
        return img.addBands(cviImgAWet).addBands(cviImgADry)

    # Green leaf index  GLI
    def agregateBandsIndexGLI(self,img):    
        print("processing agregateBandsIndexGLI") 
        gliImgWet = img.expression(
            "float((2 * b('green_median_wet') - b('red_median_wet') - b('blue_median_wet')) / (2 * b('green_median_wet') - b('red_median_wet') - b('blue_median_wet')))")\
                .rename(['gli_median_wet']).toFloat()   

        gliImgDry = img.expression(
            "float((2 * b('green_median_dry') - b('red_median_dry') - b('blue_median_dry')) / (2 * b('green_median_dry') - b('red_median_dry') - b('blue_median_dry')))")\
                .rename(['gli_median_dry']).toFloat()       
        
        return img.addBands(gliImgWet).addBands(gliImgDry)

    # Shape Index  IF 
    def agregateBandsIndexShapeI(self, img):   
        print("processing agregateBandsIndexShapeI")  
        shapeImgAWet = img.expression(
            "float((2 * b('red_median_wet') - b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') - b('blue_median_wet')))")\
                .rename(['shape_median_wet']).toFloat() 

        shapeImgADry = img.expression(
            "float((2 * b('red_median_dry') - b('green_median_dry') - b('blue_median_dry')) / (b('green_median_dry') - b('blue_median_dry')))")\
                .rename(['shape_median_dry']).toFloat()      
        
        return img.addBands(shapeImgAWet).addBands(shapeImgADry)

    # Aerosol Free Vegetation Index (2100 nm) 
    def agregateBandsIndexAFVI(self, img):  
        print("processing agregateBandsIndexAFVI")   
        afviImgAWet = img.expression(
            "float((b('nir_median_wet') - 0.5 * b('swir2_median_wet')) / (b('nir_median_wet') + 0.5 * b('swir2_median_wet')))")\
                .rename(['afvi_median_wet']).toFloat()

        afviImgADry = img.expression(
            "float((b('nir_median_dry') - 0.5 * b('swir2_median_dry')) / (b('nir_median_dry') + 0.5 * b('swir2_median_dry')))")\
                .rename(['afvi_median_dry']).toFloat()      
        
        return img.addBands(afviImgAWet).addBands(afviImgADry)

    # Advanced Vegetation Index 
    def agregateBandsIndexAVI(self, img):  
        print("processing agregateBandsIndexAVI")   
        aviImgAWet = img.expression(
            "float((b('nir_median_wet')* (1.0 - b('red_median_wet')) * (b('nir_median_wet') - b('red_median_wet'))) ** 1/3)")\
                .rename(['avi_median_wet']).toFloat()

        aviImgADry = img.expression(
            "float((b('nir_median_dry')* (1.0 - b('red_median_dry')) * (b('nir_median_dry') - b('red_median_dry'))) ** 1/3)")\
                .rename(['avi_median_dry']).toFloat()     
        
        return img.addBands(aviImgAWet).addBands(aviImgADry)

    # Bare Soil Index 
    def agregateBandsIndexBSI(self,img):   
        print("processing agregateBandsIndexBSI")   
        bsiImgWet = img.expression(
            "float(((b('swir1_median_wet') - b('red_median_wet')) - (b('nir_median_wet') + b('blue_median_wet'))) / " + 
                "((b('swir1_median_wet') + b('red_median_wet')) + (b('nir_median_wet') + b('blue_median_wet'))))")\
                .rename(['bsi_median_wet']).toFloat()

        bsiImgDry = img.expression(
            "float(((b('swir1_median_dry') - b('red_median_dry')) - (b('nir_median_dry') + b('blue_median_dry'))) / " + 
                "((b('swir1_median_dry') + b('red_median_dry')) + (b('nir_median_dry') + b('blue_median_dry'))))")\
                .rename(['bsi_median_dry']).toFloat()      
        
        return img.addBands(bsiImgWet).addBands(bsiImgDry)

    # BRBA	Band Ratio for Built-up Area  
    def agregateBandsIndexBRBA(self,img): 
        print("processing agregateBandsIndexBRBA")     
        brbaImgWet = img.expression(
            "float(b('red_median_wet') / b('swir1_median_wet'))")\
                .rename(['brba_median_wet']).toFloat()

        brbaImgDry = img.expression(
            "float(b('red_median_dry') / b('swir1_median_dry'))")\
                .rename(['brba_median_dry']).toFloat()     
        
        return img.addBands(brbaImgWet).addBands(brbaImgDry)

    # DSWI5	Disease-Water Stress Index 5
    def agregateBandsIndexDSWI5(self,img):   
        print("processing agregateBandsIndexDSWI5")   
        dswi5ImgWet = img.expression(
            "float((b('nir_median_wet') + b('green_median_wet')) / (b('swir1_median_wet') + b('red_median_wet')))")\
                .rename(['dswi5_median_wet']).toFloat() 

        dswi5ImgDry = img.expression(
            "float((b('nir_median_dry') + b('green_median_dry')) / (b('swir1_median_dry') + b('red_median_dry')))")\
                .rename(['dswi5_median_dry']).toFloat() 

        return img.addBands(dswi5ImgWet).addBands(dswi5ImgDry)

    # LSWI	Land Surface Water Index
    def agregateBandsIndexLSWI(self,img):    
        print("processing agregateBandsIndexLSWI") 
        lswiImgWet = img.expression(
            "float((b('nir_median_wet') - b('swir1_median_wet')) / (b('nir_median_wet') + b('swir1_median_wet')))")\
                .rename(['lswi_median_wet']).toFloat()

        lswiImgDry = img.expression(
            "float((b('nir_median_dry') - b('swir1_median_dry')) / (b('nir_median_dry') + b('swir1_median_dry')))")\
                .rename(['lswi_median_dry']).toFloat()      
        
        return img.addBands(lswiImgWet).addBands(lswiImgDry)

    # MBI	Modified Bare Soil Index
    def agregateBandsIndexMBI(self,img):  
        print("processing agregateBandsIndexMBI")   
        mbiImgWet = img.expression(
            "float(((b('swir1_median_wet') - b('swir2_median_wet') - b('nir_median_wet')) /" + 
                " (b('swir1_median_wet') + b('swir2_median_wet') + b('nir_median_wet'))) + 0.5)")\
                    .rename(['mbi_median_wet']).toFloat() 

        mbiImgDry = img.expression(
            "float(((b('swir1_median_dry') - b('swir2_median_dry') - b('nir_median_dry')) /" + 
                " (b('swir1_median_dry') + b('swir2_median_dry') + b('nir_median_dry'))) + 0.5)")\
                    .rename(['mbi_median_dry']).toFloat()       
        
        return img.addBands(mbiImgWet).addBands(mbiImgDry)

    # UI	Urban Index	urban
    def agregateBandsIndexUI(self,img):  
        print("processing agregateBandsIndexUI")   
        uiImgWet = img.expression(
            "float((b('swir2_median_wet') - b('nir_median_wet')) / (b('swir2_median_wet') + b('nir_median_wet')))")\
                .rename(['ui_median_wet']).toFloat() 

        uiImgDry = img.expression(
            "float((b('swir2_median_dry') - b('nir_median_dry')) / (b('swir2_median_dry') + b('nir_median_dry')))")\
                .rename(['ui_median_dry']).toFloat()       
        
        return img.addBands(uiImgWet).addBands(uiImgDry)

    # OSAVI	Optimized Soil-Adjusted Vegetation Index
    def agregateBandsIndexOSAVI(self,img): 
        print("processing agregateBandsIndexOSAVI")    
        osaviImgWet = img.expression(
            "float(b('nir_median_wet') - b('red_median_wet')) / (0.16 + b('nir_median_wet') + b('red_median_wet'))")\
                .rename(['osavi_median_wet']).toFloat() 

        osaviImgDry = img.expression(
            "float(b('nir_median_dry') - b('red_median_dry')) / (0.16 + b('nir_median_dry') + b('red_median_dry'))")\
                .rename(['osavi_median_dry']).toFloat()        
        
        return img.addBands(osaviImgWet).addBands(osaviImgDry)

    # Normalized Difference Red/Green Redness Index  RI
    def agregateBandsIndexRI(self, img):   
        print("processing agregateBandsIndexRI")      
        riImgWet = img.expression(
            "float(b('nir_median_wet') - b('green_median_wet')) / (b('nir_median_wet') + b('green_median_wet'))")\
                .rename(['ri_median_wet']).toFloat()

        riImgDry = img.expression(
            "float(b('nir_median_dry') - b('green_median_dry')) / (b('nir_median_dry') + b('green_median_dry'))")\
                .rename(['ri_median_dry']).toFloat()    
        
        return img.addBands(riImgWet).addBands(riImgDry)    

    # Tasselled Cap - brightness 
    def agregateBandsIndexBrightness(self, img):   
        print("processing agregateBandsIndexBrightness")  
        tasselledCapImgWet = img.expression(
            "float(0.3037 * b('blue_median_wet') + 0.2793 * b('green_median_wet') + 0.4743 * b('red_median_wet')  " + 
                "+ 0.5585 * b('nir_median_wet') + 0.5082 * b('swir1_median_wet') +  0.1863 * b('swir2_median_wet'))")\
                    .rename(['brightness_median_wet']).toFloat()

        tasselledCapImgDry = img.expression(
            "float(0.3037 * b('blue_median_dry') + 0.2793 * b('green_median_dry') + 0.4743 * b('red_median_dry')  " + 
                "+ 0.5585 * b('nir_median_dry') + 0.5082 * b('swir1_median_dry') +  0.1863 * b('swir2_median_dry'))")\
                    .rename(['brightness_median_dry']).toFloat() 
        
        return img.addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)
    
    # Tasselled Cap - wetness 
    def agregateBandsIndexwetness(self, img): 
        print("processing agregateBandsIndexwetness")  
        tasselledCapImgWet = img.expression(
            "float(0.1509 * b('blue_median_wet') + 0.1973 * b('green_median_wet') + 0.3279 * b('red_median_wet')  " + 
                "+ 0.3406 * b('nir_median_wet') + 0.7112 * b('swir1_median_wet') +  0.4572 * b('swir2_median_wet'))")\
                    .rename(['wetness_median_wet']).toFloat() 
        
        tasselledCapImgDry = img.expression(
            "float(0.1509 * b('blue_median_dry') + 0.1973 * b('green_median_dry') + 0.3279 * b('red_median_dry')  " + 
                "+ 0.3406 * b('nir_median_dry') + 0.7112 * b('swir1_median_dry') +  0.4572 * b('swir2_median_dry'))")\
                    .rename(['wetness_median_dry']).toFloat() 
        
        return img.addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)
    
    # Moisture Stress Index (MSI)
    def agregateBandsIndexMSI(self, img):    
        print("processing agregateBandsIndexwetness")
        msiImgWet = img.expression(
            "float( b('nir_median_wet') / b('swir1_median_wet'))")\
                .rename(['msi_median_wet']).toFloat() 

        msiImgDry = img.expression(
            "float( b('nir_median_dry') / b('swir1_median_dry'))")\
                .rename(['msi_median_dry']).toFloat() 
        
        return img.addBands(msiImgWet).addBands(msiImgDry)

    # 
    def agregateBandsIndexGVMI(self, img): 
        print("processing agregateBandsIndexGVMI")       
        gvmiImgWet = img.expression(
                        "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) " + 
                            "/ ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                        ).rename(['gvmi_median_wet']).toFloat()

        gvmiImgDry = img.expression(
                        "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) " + 
                            "/ ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                        ).rename(['gvmi_median_dry']).toFloat()   
    
        return img.addBands(gvmiImgWet).addBands(gvmiImgDry) 
    

    def agregateBandsIndexsPRI(self, img): 
        print("processing agregateBandsIndexsPRI")       
        priImgWet = img.expression(
                                "float((b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') + b('blue_median_wet')))"
                            ).rename(['pri_median_wet'])   
        spriImgWet =   priImgWet.expression(
                                "float((b('pri_median_wet') + 1) / 2)").rename(['spri_median_wet']).toFloat()

        priImgDry = img.expression(
                                "float((b('green_median_dry') - b('blue_median_dry')) / (b('green_median_dry') + b('blue_median_dry')))"
                            ).rename(['pri_median_dry'])   
        spriImgDry =   priImgDry.expression(
                                "float((b('pri_median_dry') + 1) / 2)").rename(['spri_median_dry']).toFloat()
    
        return img.addBands(spriImgWet).addBands(spriImgDry)
    

    def agregateBandsIndexCO2Flux(self, img):     
        print("processing agregateBandsIndexCO2Flux")    
        co2FluxImg_wet = img.select('ndvi_median_wet').multiply(img.select('spri_median_wet')).rename(['co2flux_median_wet'])   
        
        co2FluxImg_dry = img.select('ndvi_median_dry').multiply(img.select('spri_median_dry')).rename(['co2flux_median_dry']) 
        
        return img.addBands(co2FluxImg_wet).addBands(co2FluxImg_dry)


    def agregateBandsTexturasGLCM(self, img):  
        print("processing agregateBandsTexturasGLCM")        
        img = img.toInt()                
        textura2 = img.select('nir_median_wet').glcmTexture(3)  
        contrastnirWet = textura2.select('nir_median_wet_contrast').toUint16()
        textura2Dry = img.select('nir_median_dry').glcmTexture(3)  
        contrastnirDry = textura2Dry.select('nir_median_dry_contrast').toUint16()
        #
        textura2R = img.select('red_median_wet').glcmTexture(3)  
        contrastred = textura2R.select('red_median_wet_contrast').toFloat()
        textura2RDry = img.select('red_median_dry').glcmTexture(3)  
        contrastredDry = textura2RDry.select('red_median_dry_contrast').toFloat()

        return  img.addBands(contrastnirWet).addBands(contrastred
                        ).addBands(contrastnirDry).addBands(contrastredDry)

    #endregion
    # https://code.earthengine.google.com/d5a965bbb6b572306fb81baff4bd401b
    def get_class_maskAlerts(self, yyear):
        #  get from ImageCollection 
        maskAlertyyear = ee.ImageCollection(self.options['asset_alerts']).filter(ee.Filter.eq('yearDep', yyear)
                                ).reduce(ee.Reducer.max()).eq(0).rename('mask_alerta')

        return maskAlertyyear        

    def get_class_maskFire(self, yyear):
        maskFireyyear = ee.Image(self.options['asset_fire']).select("burned_area_" + str(yyear)
                                    ).unmask(0).eq(0).rename('mask_fire')

        return maskFireyyear

    def CalculateIndice(self, imagem):

        # band_feat = [
        #         "ratio","rvi","ndwi","awei","iia","evi",
        #         "gcvi","gemi","cvi","gli","shape","afvi",
        #         "avi","bsi","brba","dswi5","lswi","mbi","ui",
        #         "osavi","ri","brightness","wetness","gvmi",
        #         "nir_contrast","red_contrast"
        #     ]        
        
        imageW = self.agregateBandsIndexEVI(imagem)
        # print("  => ",  imageW.bandNames().getInfo())
        imageW = self.agregateBandsIndexRATIO(imageW)  #
        imageW = self.agregateBandsIndexRVI(imageW)    #    
        imageW = self.agregateBandsIndexWater(imageW)  #   
        imageW = self.agregateBandsIndexGVMI(imageW)
        imageW = self.AutomatedWaterExtractionIndex(imageW)  #      
        imageW = self.IndiceIndicadorAgua(imageW)    #      
        imageW = self.agregateBandsIndexGCVI(imageW)   #   
        imageW = self.agregateBandsIndexGEMI(imageW)
        imageW = self.agregateBandsIndexCVI(imageW) 
        # print("  => ",  imageW.bandNames().getInfo())
        imageW = self.agregateBandsIndexGLI(imageW) 
        imageW = self.agregateBandsIndexShapeI(imageW) 
        imageW = self.agregateBandsIndexAFVI(imageW) 
        imageW = self.agregateBandsIndexAVI(imageW)         
        imageW = self.agregateBandsIndexBSI(imageW) 
        imageW = self.agregateBandsIndexBRBA(imageW) 
        # print("  => ",  imageW.bandNames().getInfo())
        imageW = self.agregateBandsIndexDSWI5(imageW) 
        imageW = self.agregateBandsIndexLSWI(imageW)         
        imageW = self.agregateBandsIndexMBI(imageW) 
        imageW = self.agregateBandsIndexUI(imageW) 
        imageW = self.agregateBandsIndexRI(imageW) 
        
        imageW = self.agregateBandsIndexOSAVI(imageW)  #     
        imageW = self.agregateBandsIndexwetness(imageW)   #   
        # print("  => ",  imageW.bandNames().getInfo())
        imageW = self.agregateBandsIndexBrightness(imageW)  #       
        imageW = self.agregateBandsTexturasGLCM(imageW)     #
        print(" imagem FINAL => ",  imageW.bandNames().getInfo())

        return imageW #.select(band_feat)# .addBands(imageF)    
    

    def processing_classify_models(self, area_classificar):
        # selectBacia = ftcol_bacias.filter(ee.Filter.eq('nunivotto3', _nbacia)).first()
        # https://code.earthengine.google.com/2f8ea5070d3f081a52afbcfb7a7f9d25 


        nameFeatROIsv2 = self.options['nom_vector_coletav2'] 
        nameFeatROIsv3 = self.options['nom_vector_coletav3']  # essas são amostras complementares
        nameFeatROIsCampo =  self.options['nom_ROIs_coletaCampo']

        if self.classificador == 'gradient_tree_boost':
            nameFeatROIsv2 = nameFeatROIsv2.replace('_coletadas_', '_ptos_samples_')
            nameFeatROIsv3 = nameFeatROIsv3.replace('_coletadas_', '_ptos_samples_')
        
        print("path" , self.options['inAssetROIsPolg'] + '/' + nameFeatROIsv2)
        print(" and" , self.options['inAssetROIsPolg'] + '/' + self.options['nom_vector_coletav3'])

        ROIs_toTrain = ee.FeatureCollection(self.options['inAssetROIsPolg'] + '/' + nameFeatROIsv2).merge(
                            ee.FeatureCollection(self.options['inAssetROIsPolg'] + '/' + nameFeatROIsv3))

        if area_classificar == 'urbano':
            # mascara de áreas de Urbano 
            imMask = ee.Image(self.options['asset_geodatin_urbano'])
            lstCC = [18,29]
            ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.inList('classe', lstCC).Not())
        elif area_classificar == 'agropecuaria':
            lstCC = [24,29]
            # mascara de áreas de Agropecuarias 
            imMask = ee.Image(self.options['asset_geodatin_agro'])
            ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.inList('classe', lstCC).Not())
        elif area_classificar == 'areasCampestres':
            # https://code.earthengine.google.com/c07aea4888f64bbb3c3cd9efb45d94c3
            # mascara de áreas de Areas Campestres 
            # imMask = ee.Image(self.options['asset_geodatin_campo'])
            # remove areas de Agro e 
            # mascara de outras áreas  
            imMaskAgro = ee.Image(self.options['asset_geodatin_agro']).unmask(0).add(
                            ee.Image(self.options['asset_geodatin_urbano']).unmask(0)).gt(0)
            
            imgGEDI = ee.ImageCollection(self.options['asset_gedi']).mosaic().clip( self.regionInterest);
            maskGEDI = imgGEDI.eq(0)
            # imMask = imMask.add(maskGEDI).eq(1)
            imMask = maskGEDI.subtract(imMaskAgro).gt(0)
            # {'12': 31874, '15': 36625, '25': 11860, '29': 4473, '33': 48982, '4': 93738}
            # distribuidos por :  {'1': 1800, '15': 3945, '25': 3375, '29': 3630, '33': 2400, '4': 5625}
            # lstCC = [3, 18, 24, 29, 15, 4, 33, 25]   
            lstCC = [3, 18, 24]         
            baseROIs_toTrain = ROIs_toTrain.filter(ee.Filter.inList('classe', lstCC).Not())
            ROIsCampo = ee.FeatureCollection(self.options['inAssetROIsPolg'] + '/' + nameFeatROIsCampo)
            ROIsCampo = ROIsCampo.map(lambda feat: feat.set('classe', 12))
            # baseROIs_toTrain = baseROIs_toTrain.merge(
            #                         ROIs_toTrain.filter(ee.Filter.eq('classe', 29)).limit(300)).merge(
            #                             ROIs_toTrain.filter(ee.Filter.eq('classe', 15)).limit(800)).merge(
            #                                 ROIs_toTrain.filter(ee.Filter.eq('classe', 4)).limit(800)).merge(
            #                                     ROIs_toTrain.filter(ee.Filter.eq('classe', 33)).limit(300)).merge(
            #                                         ROIs_toTrain.filter(ee.Filter.eq('classe', 25)).limit(800))

            ROIs_toTrain = baseROIs_toTrain.merge(ROIsCampo) # .limit(2400)

        else:
            # mascara de outras áreas  
            imMask = ee.Image(self.options['asset_geodatin_agro']).unmask(0).add(
                            ee.Image(self.options['asset_geodatin_urbano']).unmask(0)).eq(0)

            lstCC = [18,24]
            ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.inList('classe', lstCC).Not())
        
        
        print("numero de pontos: ", ROIs_toTrain.size().getInfo())  
        print("distribuidos por : ", ROIs_toTrain.aggregate_histogram('classe').getInfo())
        # sys.exit()
        images_mosaic = self.imgMosaic.updateMask(imMask)        
        img_recMosaicnewB = self.CalculateIndice(images_mosaic)

        print("coletando todos os indexs ")
        bndAdd = img_recMosaicnewB.bandNames().getInfo()
        print(f"know bands names {len(bndAdd)}")

        ###############################################################
        # print(ROIs_toTrain.size().getInfo())
        # ROIs_toTrain_filted = ROIs_toTrain.filter(ee.Filter.notNull(bandas_imports))
        # print(ROIs_toTrain_filted.size().getInfo())
        # lsAllprop = ROIs_toTrain_filted.first().propertyNames().getInfo()
        # print('PROPERTIES FEAT = ', lsAllprop)
        #cria o classificador com as especificacoes definidas acima 
        sufixo = self.options['dictClassModel'][self.classificador]
        classificador_geral = None
        if self.classificador == 'random_forest':        
            classifierRF = ee.Classifier.smileRandomForest(**self.options['pmtRF'])\
                                        .train(ROIs_toTrain, 'classe', self.bandas_selected)
            classifiedRF = img_recMosaicnewB.classify(classifierRF, 'classification_2020')
            classificador_geral = classifiedRF
            print("classification with Random Forest model")

            # print("pmtros Classifier Ajustado ==> ", pmtroClass)
        elif self.classificador == 'gradient_tree_boost':
            # ee.Classifier.smileGradientTreeBoost(numberOfTrees, shrinkage, samplingRate, maxNodes, loss, seed)
            classifierGTB = ee.Classifier.smileGradientTreeBoost(**self.options['pmtGTB'])\
                                        .train(ROIs_toTrain, 'classe', self.bandas_selected)
            classifiedGTB = img_recMosaicnewB.classify(classifierGTB, 'classification_2020')
            classificador_geral = classifiedGTB
            print("classification with Gradiente Tree Boost model")

        else:
            # ee.Classifier.libsvm(decisionProcedure, svmType, kernelType, shrinking, degree, 
            # gamma, coef0, cost, nu, terminationEpsilon, lossEpsilon, oneClass)
            classifierSVM = ee.Classifier.libsvm(**self.options['pmtSVM'])\
                                        .train(ROIs_toTrain, 'classe', self.bandas_imports)

            classifiedSVM = img_recMosaicnewB.classify(classifierSVM, 'classification_2020')
            classificador_geral = classifiedSVM
            print("classification with Suppert Vector Machine model")
        
        classificador_geral = ee.Image(classificador_geral).set(
            'classificador', sufixo,
            'version', self.options['version'],
            'biome', self.options['bioma'],
            'layer', area_classificar,
            'collection', 'beta',
            'sensor', 'sentinel',
            'source', 'geodatin'
        )
        print("passo")
        nomec = "mapa_SC-24-V-D_" + str(self.options['subgrade']) + "_2020_" + sufixo + "_v" + self.options['version'] + '_' + area_classificar
        print("vai salvar ", nomec)
        # exporta bacia
        self.processoExportar(classificador_geral, self.regionInterest, nomec) 
                   
 


    #exporta a imagem classificada para o asset
    def processoExportar(self, mapaRF, regionB, nameB):
        idasset =  self.options['output_class'] + "/" + nameB
        print("saving ")
        optExp = {
            'image': mapaRF, 
            'description': nameB, 
            'assetId':idasset, 
            'region':regionB, #['coordinates']
            'scale': 10, 
            'maxPixels': 1e13,
            "pyramidingPolicy":{".default": "mode"}
        }
        
        task = ee.batch.Export.image.toAsset(**optExp)
        task.start() 
        print("saving ")
        print("salvando ... " + nameB + "..!")
        # print(task.status())
        for keys, vals in dict(task.status()).items():
            print ( "  {} : {}".format(keys, vals))



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
    }    
}

#============================================================
#========================METODOS=============================
#============================================================

def gerenciador(cont):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(param['conta'][str(cont)]))        
        gee.switch_user(param['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= param['numeroTask'], return_list= True)        
    
    elif cont > param['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont

dictClas:{
    '3': 'Formação Florestal',
    '4': 'Formação Savânica',
    '12': 'Formação Campestre',
    '15': 'Pastagem',
    '18': 'Agricultura',
    '21': 'Mosaico de Usos',
    '24': 'Area Urbana',
    '25': 'Outras Áreas não Vegetadas',
    '29': 'Afloramento Rochoso',
    '33': 'Água'
}

mapaUrbano = False
mapaAgro = False
mapaRestante = False
mapaCampestre = True
# 'random_forest'
# 'gradient_tree_boost'
# 'support_vector_machine':
oClassificador = 'random_forest'
year_select = 2020
regiaoCaat = ee.FeatureCollection(param['subGridsAsset']).filter(
                    ee.Filter.eq("grid", param['carta_selected'])).filter(
                          ee.Filter.eq("subgrid_id", param['subgrade'])) \
                        .geometry();

# cont = gerenciador(12)
# sys.exit()
objetoMosaic_exportROI = ClassMosaic_indexs_Spectral(regiaoCaat, year_select, oClassificador)
# geobacia, colAnos, nomeBacia, dict_nameBN4
# processando agora por camadas dentro dos mapas de referencias 
if mapaUrbano:
    area_to_classify = 'urbano'
    objetoMosaic_exportROI.processing_classify_models(area_to_classify)
#============================================================#
if mapaAgro:
    area_to_classify = 'agropecuaria'
    objetoMosaic_exportROI.processing_classify_models(area_to_classify)
#============================================================#
if mapaRestante:
    area_to_classify = 'outras_areas'
    objetoMosaic_exportROI.processing_classify_models(area_to_classify)
# cont = gerenciador(cont, param)
#============================================================#
if mapaCampestre:
    area_to_classify = 'areasCampestres'
    objetoMosaic_exportROI.processing_classify_models(area_to_classify)