'''
Created on Oct 1, 2010

@author: guillaume.aubert@eumetsat.int
'''

import csv
import simplejson


class Lookup(dict):
    """
    a dictionary which can lookup value by key, or keys by value
    """
    def __init__(self, items=[]):
        """items can be a list of pair_lists or a dictionary"""
        dict.__init__(self, items)
 
    def get_key(self, value):
        """find the key(s) as a list given a value"""
        return [item[0] for item in self.items() if item[1] == value]
 
    def get_value(self, key):
        """find the value given a key"""
        return self[key]

class CSV2JSONRoddExtractor(object):
    '''
     Extract Data from the previous RODD DB
    '''
    
    def __init__(self, a_directory):
        """ constructor """
        
        self._root_dir = a_directory
    
    def extract_service_dirs(self):
        """ extract service dirs """
        csv_services  = csv.DictReader(open('%s/tbl_service.csv' %(self._root_dir)))
        
        # need also the channels
        csv_channels = csv.DictReader(open('%s/tbl_channels.csv' %(self._root_dir)))
        
        #create ID to channel index
        channels_idx = {}
        for row in csv_channels:
            channels_idx[row['ID']] = row
            
        result = { "service_dirs" : [] }
        
        for row in csv_services:
            name    = row['service_directory']
            channel = channels_idx[row['channel']]['channel']
            
            result["service_dirs"].append({ 
                                             "name"    : name,
                                             "channel" : channel
                                           })
        
        return result

    def extract_channels(self):
        """ extract channels """
        
        csv_channels = csv.DictReader(open('%s/tbl_channels.csv' %(self._root_dir)))
        
        result = { "channels" : [] }
        for row in csv_channels:
            name              = row["channel"]
            multicast_address = row["multicast_address"]
            min_rate          = row["min_rate"]
            max_rate          = row["max_rate"]
            channel_function  = row["channel_function"]
            
            result["channels"].append( { 
                                        "name" : name,
                                        "multicast_address":multicast_address,
                                        "min_rate": min_rate,
                                        "max_rate": max_rate,
                                        "channel_function": channel_function
                                       })
        
        return result
    
    def extract_products(self):
        """ extract the products """
        
            
        
if __name__ == '__main__':
    
    root_dir = "/homespace/gaubert/ecli-workspace/rodd/etc/data/rodd-data/csv"
    
    extractor = CSV2JSONRoddExtractor(root_dir)
    
    #json = extractor.extract_service_dirs()
    
    #print("json %s\n" %(json))
    
    #json2 = extractor.extract_channels()
    
    #print("json2 %s\n" %(json2))
    
    #merge dicts
    #z = dict(json, **json2)
    
    json3 = extractor.extract_products()
    
    #print("z = %s\n" % (z))
    
    print("z = %s\n" % (simplejson.dumps(z, sort_keys=True)))
    
    simplejson.dump(z,open("/tmp/dump.json","w"),sort_keys=True, indent=True)
