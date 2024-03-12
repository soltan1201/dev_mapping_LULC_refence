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
        "median_blue_median_wet": float(1096.0578160344407),
        "median_green_median_wet": float(1098.709489027003),
        "median_red_median_wet": float(976.5168696816625),
        "median_nir_median_wet": float(2488.803981135233),
        "median_swir1_median_wet": float(2590.708057737918),
        "median_swir2_median_wet": float(1491.7623228609739),
        "median_blue_median_dry": float(1172.7243955891456),
        "median_green_median_dry": float(1169.1687031130916),
        "median_red_median_dry": float(1279.6717378018277),
        "median_nir_median_dry": float(2019.8880081974671),
        "median_swir1_median_dry": float(3143.650563677744),
        "median_swir2_median_dry": float(2093.1297194020954),
        "stdDev_blue_median_wet": float(216.81962108751355),
        "stdDev_green_median_wet": float(259.92685500367475),
        "stdDev_red_median_wet": float(375.5613485310523),
        "stdDev_nir_median_wet": float(438.60626940637314),
        "stdDev_swir1_median_wet": float(513.3187279778745),
        "stdDev_swir2_median_wet": float(466.0627768106192),
        "stdDev_blue_median_dry": float(142.54110653132767),
        "stdDev_green_median_dry": float(215.4591413723328),
        "stdDev_red_median_dry": float(346.9520939981621),
        "stdDev_nir_median_dry": float(451.598842719077),
        "stdDev_swir1_median_dry": float(577.197374855401),
        "stdDev_swir2_median_dry": float(498.71129520994134)   
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
        'nom_vector_Campos': 'poligons_area_campestre',
        'nom_vector_SavCampSol': "poligons_area_campestre_solo_savana",
        # projects/mapbiomas-arida/coletaMapaRef/amostras_coletadas_mapa_referencia_2022_S2_v2
        'carta_selected': "SC-24-V-D",
        'subgrade': 0,
        'lsClasse': [3, 4,12,15,18,24,25,29,33],
    }

    def __init__(self, myGeom, nyear):

        self.regionInterest = ee.Geometry(myGeom)
        imgColGeodatin = ee.ImageCollection(self.options['asset_geodatin_next']).merge(
                            ee.ImageCollection(self.options['asset_geodatin_work'])).filter(
                                ee.Filter.eq('year', nyear)).filterBounds(self.regionInterest);
        
        self.imgMosaic = imgColGeodatin.map(lambda img: self.process_normalized_img(img))
                                                    
        # print("  ", self.imgMosaic.size().getInfo())
        print("see band Names of the first imagem")
        print("     " ,ee.Image(self.imgMosaic.first()).bandNames().getInfo())
        self.imgMosaic = self.imgMosaic.median()
        
        
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
                .rename(['evi_median_wet']).toFloat()  

        eviImgDry = img.expression(
            "float(2.4 * (b('nir_median_dry') - b('red_median_dry')) / (1 + b('nir_median_dry') + b('red_median_dry')))")\
                .rename(['evi_median_dry']).toFloat()
  
        
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
        co2FluxImg_wet = img.select('ndvi_median_wet').multiply(img.select('spri_median_wet')).rename(['co2flux_median_wet']).toFloat()   
        
        co2FluxImg_dry = img.select('ndvi_median_dry').multiply(img.select('spri_median_dry')).rename(['co2flux_median_dry']).toFloat() 
        
        return img.addBands(co2FluxImg_wet).addBands(co2FluxImg_dry)


    def agregateBandsTexturasGLCM(self, image):  
        print("processing agregateBandsTexturasGLCM")        
        img = ee.Image(image).multiply(10000).toInt32();                

        texturaNirDry = img.select('nir_median_dry').glcmTexture(3)  
        savgNirDry = texturaNirDry.select('nir_median_dry_savg').divide(10000).toFloat()  # suma dos promedios
        dissNirDry = texturaNirDry.select('nir_median_dry_diss').divide(1000).toFloat()  #  dissimilarity
        contrastNirDry = texturaNirDry.select('nir_median_dry_contrast').divide(1000000).toFloat() # metrica de contraste
        varNirDry = texturaNirDry.select('nir_median_dry_var').divide(1000000).toFloat()  # suma da varianza
        # print(texturaNirDry);
    
        texturaRedDry = img.select('red_median_dry').glcmTexture(2)  
        savgRedDry = texturaRedDry.select('red_median_dry_savg').divide(10000).toFloat()
        dissRedDry = texturaRedDry.select('red_median_dry_diss').divide(1000).toFloat()
        contrastRedDry = texturaRedDry.select('red_median_dry_contrast').divide(1000000).toFloat()
        varRedDry = texturaRedDry.select('red_median_dry_var').divide(1000000).toFloat()
    
        texturaSwir1Dry = img.select('swir1_median_dry').glcmTexture(3) 
        savgSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_savg').divide(10000).toFloat()
        dissSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_diss').divide(1000).toFloat()
        contrastSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_contrast').divide(1000000).toFloat()
        varSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_var').divide(1000000).toFloat()

        return  image.addBands(savgNirDry).addBands(contrastNirDry).addBands(savgRedDry
                            ).addBands(contrastRedDry).addBands(savgSwir1Dry).addBands(contrastSwir1Dry
                                    ).addBands(dissNirDry).addBands(dissRedDry).addBands(dissSwir1Dry
                                            ).addBands(varNirDry).addBands(varRedDry).addBands(varSwir1Dry)

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
    
    def exportar_spectral_values_fromMosaic(self, coletaCampos):

        # colecao responsavel por executar o controle de execucao, caso optem 
        # por executar o codigo em terminais paralelos,
        # ou seja, em mais de um terminal simultaneamente..
        # caso deseje executar num unico terminal, deixar colecao vazia.        
        # colecaoPontos = ee.FeatureCollection([])
        # lsNoPtos = []
        if coletaCampos == 'campos' :
            nameFeatROIs = self.options['nom_vector_Campos']
        elif coletaCampos == 'todas_classes':
            nameFeatROIs = self.options['nom_vector_coleta']
        else:
            nameFeatROIs = self.options['nom_vector_SavCampSol'] 

        
        # nameFeatROIs = nameFeatROIs.replace('_coletadas_', '_ptos_samples_')

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
        ptosTemp = ee.Image(img_recMosaicnewB).toFloat().sampleRegions(
                            collection= featROIsPol,
                            properties= ['classe'],
                            scale= 10,
                            tileScale= 1,
                            geometries= True
                        )
        # insere informacoes em cada ft
        # ptosTemp = ptosTemp.filter(ee.Filter.notNull(['blue_median_wet']))
        # merge com colecoes anteriores
        # colecaoPontos = colecaoPontos.merge(ptosTemp)            
        # sys.exit()
        name_exp = nameFeatROIs + "_points"  
        self.save_ROIs_toAsset(ee.FeatureCollection(ptosTemp), name_exp)        
    
    # salva ftcol para um assetindexIni
    def save_ROIs_toAsset(self, collection, name):

        optExp = {
            'collection': ee.FeatureCollection(collection),
            'description': name,
            'assetId': self.options['outAssetROIs'] + "/" + name
        }

        task = ee.batch.Export.table.toAsset(**optExp)
        task.start()
        print("exportando ROIs to Asset $s ...!", name)
        
        optExp = {
            'collection': ee.FeatureCollection(collection), 
            'description': name, 
            'folder': 'ptosSHP'         
        };
        taskD = ee.batch.Export.table.toDrive(**optExp);
        taskD.start()
        print("exportando ROIs to Driver Google $s ...!", name)


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
coletCampo =  'todas_classes' # 'campo_outros', 'todas_classes', 'campos'
if coletCampo == 'todas_classes':
    regiaoCaat = ee.FeatureCollection(param['subGridsAsset']).filter(
                        ee.Filter.eq("grid", param['carta_selected'])).filter(
                            ee.Filter.eq("subgrid_id", param['subgrade'])
                            ).geometry();
else:
    regiaoCaat = ee.FeatureCollection(param['subGridsAsset']).filter(
                        ee.Filter.eq("grid", param['carta_selected'])
                            ).geometry();

# cont = gerenciador(0, param)

objetoMosaic_exportROI = ClassMosaic_indexs_Spectral(regiaoCaat, year_select)
# geobacia, colAnos, nomeBacia, dict_nameBN4
objetoMosaic_exportROI.exportar_spectral_values_fromMosaic(coletCampo)
# cont = gerenciador(cont, param)
