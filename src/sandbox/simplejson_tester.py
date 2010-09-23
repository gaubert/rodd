'''
Created on Sep 23, 2010

@author: gaubert
'''

import simplejson as json

if __name__ == '__main__':
    
    product1 = '["foo", {"bar":["baz", null, 1.0, 2]}]'
    
    product2 = '{"product":{"name":"ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)","uid":"EO:EUM:DAT:METOP:ASCSZR1B","description":"The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.","distribution":["EUMETSAT Data Centre","GTS","EUMETCast-Europe"],"eumetcast-info":{"files":[{"name":"ascat_bufr","regexpr":"ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr","size":"200KB","type":"bufr","frequency":"480 per day","service_dir":"EPS-METOP-ASCA-L1"},{"name":"ascat_nativr","regexpr":"ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z","size":"740KB","type":"native","frequency":"480 per day","service_dir":"EPS-METOP-ASCA-L1"}]},"gts-info":{"files":[{"name":"ascat_bufr","regexpr":"ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr","size":"200KB","type":"bufr","frequency":"480 per day"}]},"data-centre-info":{"files":[{"name":"ascat_native_large","size":"25MB","type":"native","frequency":"15 per day"},{"name":"ascat_hdf5eps","size":"27MB","type":"hdf5eps","frequency":"15 per day"}]}},"service_dirs":[{"name":"EPS-METOP-ASCA-L1","channel":"EPS-3"}],"channels":[{"name":"EPS-3","freq":"afrequence"}]}'

    
    

    print(json.dumps(json.loads(product2),separators=(',',':')))
