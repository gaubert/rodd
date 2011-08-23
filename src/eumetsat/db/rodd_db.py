'''
Created on Sep 29, 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy
import decimal
import simplejson as json
import time

from sqlalchemy.orm import mapper, relationship

import eumetsat.common.logging_utils as logging
from eumetsat.db import connections
from eumetsat.common.collections import OrderedDict




class Product(object): #pylint:disable-msg=R0903,R0902
    """ Product Object """
    
    LOGGER = logging.LoggerFactory.get_logger("Product")
    
    def __init__(self, title, internal_id, description, disseminated, status): #pylint:disable-msg=R0913
        self.rodd_id            = None
        self.title              = title
        self.internal_id        = internal_id
        self.description        = description
        self.is_disseminated    = disseminated
        self.status             = status
        
        self.file_infos         = []
        self._dis_type_cache    = {}
        self._file_index        = None
  
    def __repr__(self):
        
        self._populate_type_cache()
        
        return "<Product(%s'%s', '%s', '%s', '%s', '%s', files= [ eumetcast = ('%s'), gts = ('%s'), data_centre= ('%s'), geonetcast = ('%s') )>" \
               % ( (( "'rodd_id:%s', " % (self.rodd_id)) if self.rodd_id else ""), \
                     self.title, self.internal_id, \
                     self.description ,\
                     self.is_disseminated, \
                     self.status, \
                     self._dis_type_cache[DistributionType.EUMETCAST], \
                     self._dis_type_cache[DistributionType.GTS], \
                     self._dis_type_cache[DistributionType.DATACENTRE], \
                     self._dis_type_cache[DistributionType.GEONETCAST])
               
    def _populate_type_cache(self):
        """ separate files by distribution types """
        
        result = {}     
        for finfo in self.file_infos:
            for the_type in finfo.dis_types:
                if the_type not in result["distribution"]:
                    result["distribution"].append(type)
                
                result[type]["files"].append(finfo.jsonize())
        
        self._dis_type_cache = result
        return self._dis_type_cache
    
    def update(self, a_prod_dict, a_session):
        """ Update attributes of the product. 
            Policy is to replace all attributes with existing ones and supress non present ones, 
        """
        
        
        if a_prod_dict.get('name', None):
            self.title = a_prod_dict['name']
            
        if a_prod_dict.get('description', None):
            self.description = a_prod_dict['description']
        
        file_dict = {}
        
        new_file_infos = []
        
        for the_type in DistributionType.TYPES:
            
            for a_file in a_prod_dict.get(the_type, { 'files' : [] }).get('files', []):
        
                finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()    
                if not finfo:    
                    #create file object
                    finfo = FileInfo(  a_file["name"], \
                                       a_file.get("regexpr", ""), \
                                       a_file["size"], \
                                       a_file["type"])
                    
            
                    #finfo.dis_types.append(ARCHIVE_DIS_TYPE)
                    diss_type = a_session.query(DistributionType).filter_by(name=the_type).first() 
                    finfo.dis_types.append(diss_type)
                                
                #add in new_file_infos   
                new_file_infos.append(finfo)
                file_dict[a_file['name']] = finfo
                
        # Replace the current file_info with new_file_info if not empty
        self.file_infos = new_file_infos
    
    def update_files(self, a_session, a_file_data):
        """ update existing files """
        
        for a_file in a_file_data.get('files', []):
            finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()
            if finfo:

                # update file
                finfo.update(a_session, a_file)
            else:
                Product.LOGGER.info("file %s not present in %s" % (a_file['name'], self.rodd_id))
        
    
    def add_files(self, a_session, a_file_data):
        """ add one or multiple files. 
            If the file already exists, replace its content with the new content
        """
        for a_file in a_file_data.get('files', []):
            finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()
            if not finfo:
                # add new file
                finfo = FileInfo(    a_file["name"], \
                                     a_file.get("regexpr", ""), \
                                     a_file["size"], \
                                     a_file["type"])
                
                finfo.add_missing_dis_types(a_file['dis_type'])
                
                self.file_infos.append(finfo)
                
            else:
                # update file
                finfo.update(a_session, a_file)
    
    
    def get_index(self):
        """
           return the file index
        """
        try:
            return self._file_index
        except AttributeError:
            self._file_index = {}
            
            for fileinfo in self.file_infos:
                if fileinfo.name in self._file_index:
                    self._file_index[fileinfo.name][0] = fileinfo.dis_types
                else:
                    self._file_index[fileinfo.name] = (fileinfo.dis_types, fileinfo)
            
            return self._file_index
           
                
    
    def contains_file(self, name):
        """ check if the product contains the file.
            Return the distribution type if yes otherwise None 
        """
        return self.get_index().get(name)
    
    def get_files_from(self, diss_type):
        """ get all the files for a particular diss_type """
        self._populate_type_cache()
        
        return self._dis_type_cache.get(diss_type, [])
        
        
    def jsonize(self):
        """ jsonize Product """
        result = OrderedDict()
        
        result["name"]         = self.title 
        result["uid"]          = self.internal_id
        result["description"]  = self.description
        result["distribution"] = []
        
        
        result[DistributionType.EUMETCAST]   = { "files": [] }
        result[DistributionType.GTS]         = { "files": [] }
        result[DistributionType.DATACENTRE]  = { "files": [] }
        result[DistributionType.GEONETCAST]  = { "files": [] }
        result[DistributionType.DIRECT]      = { "files": [] }
        
        for finfo in self.file_infos:
            for the_type in finfo.dis_types:
                if the_type.name not in result["distribution"]:
                    result["distribution"].append(the_type.name)
                
                probe_t1 = time.time()
                result[the_type.name]["files"].append(finfo.jsonize())
                probe_t2 = time.time()
       
                Product.LOGGER.info("#### jsonize finfo %f\n" %(probe_t2-probe_t1))
            
        return result
        
class ServiceDir(object): #pylint:disable-msg=R0903
    """ServiceDir object """
    def __init__(self, name, channel):
        self.serv_id     = None
        self.name        = name
        self.channel     = channel
    
    def __repr__(self):
        return "<ServiceDir(%s'%s', '%s')>" % ( (("'serv_id:%s', " % (self.serv_id)) if self.serv_id else ""), \
                                                self.name, \
                                                self.channel)
    
    def jsonize(self):
        """ jsonize """
        
        return { 'name' : self.name,
                 'channel' : self.channel.name if self.channel else ""
               }
    
class DistributionType(object):
    """ DistributionType object """
    
    EUMETCAST   = 'eumetcast-info'
    GTS         = 'gts-info'
    GEONETCAST  = 'geonetcast-info'
    DATACENTRE  = 'data-centre-info'
    DIRECT      = 'direct-info'
    
    TYPES = [EUMETCAST, GTS, GEONETCAST, DATACENTRE, DIRECT]
    
    WORLD = 'world'
    
    GEO   = [WORLD, 'europe', 'africa', 'america']
    
    @classmethod
    def create_distribution_type(cls, dis_type_name):
        """ factory method controlling that the distribution type exists """
        if dis_type_name not in DistributionType.TYPES:
            raise Exception("%s is not a valid distribution type. Supported distribution types are %s\n" % (dis_type_name, DistributionType.TYPES) )
        
        return DistributionType(dis_type_name, DistributionType.WORLD)
    
    def __init__(self, name, geo):
        self.dis_id   = None
        self.name     = name
        self.geo      = geo
    
    def __repr__(self):
        return "<DistributionType('%s','%s')>" % (self.name, self.geo)
    
    def __eq__(self, ext_obj):
        """ equality operator """
        
        #if string try to compare the value with the name
        #this isn't nice but practical
        if type(ext_obj) == type(""):
            return (ext_obj == self.name)
        else:    
            #return ( (ext_obj.name == self.name) and (ext_obj.geo_reg == self.geo_reg) )
            return ( (ext_obj.name == self.name) )
        
    def jsonize(self):
        """ jsonize """
        
        #result = { 'name' : self.name }
        return self.name
        
    
class Channel(object): #pylint:disable-msg=R0903
    """ Channel object """
    
    def __init__(self, name, address, min_rate, max_rate, channel_function): #pylint:disable-msg=R0913
        """ constructor """
        self.chan_id           = None
        self.name              = name
        self.multicast_address = address
        self.min_rate          = min_rate
        self.max_rate          = max_rate
        self.channel_function  = channel_function
        
    def __repr__(self):
        return "<Channel(%s'%s', '%s', '%s', '%s', '%s')>" % ( (( "'chan_id:%s', " % (self.chan_id)) if self.chan_id else ""), \
                                                              self.name, self.multicast_address, self.min_rate, self.max_rate, self.channel_function)
    
    def jsonize(self):
        """ jsonize """
        result = {}
        
        result['name']              = self.name
        result['multicast_address'] = self.multicast_address
        
        # given as decimal by sqlalchemy to ROUND_UP to get only integer values 
        #result['min_rate']            = str(decimal.Decimal(self.min_rate).quantize(decimal.Decimal('1')))
        #result['max_rate']            = str(decimal.Decimal(self.max_rate).quantize(decimal.Decimal('1')))
        result['min_rate']            = str(self.min_rate)
        result['max_rate']            = str(self.max_rate)
        
        
        result['channel_function']    = self.channel_function
        
        return result
        

class FileInfo(object):
    """ FileInfo object """
    
    LOGGER = logging.LoggerFactory.get_logger("FileInfo")
    
    def __init__(self, name, reg_expr, size, a_type):
         
        self.file_id       = None
        self.name          = name
        self.reg_expr      = reg_expr
        self.size          = size
        self.type          = a_type
        self.service_dirs  = []
        self.dis_types     = []
    
    def __repr__(self):
        return "<FileInfo(%s'%s','%s', '%s', '%s', '%s')>" % ((( "'file_id:%s', " % (self.file_id)) if self.file_id else ""), \
                                                               self.name, \
                                                               self.reg_expr, \
                                                               self.size, \
                                                               self.type, \
                                                               self.service_dirs)
        
    def jsonize(self):
        """ jsonize """
        result = {"service_dir" : [], "dis_type" : []}
        
        result["name"]        = self.name
        result["regexpr"]     = self.reg_expr
        result["size"]        = self.size
        result["type"]        = self.type
        
        for service_dir in self.service_dirs:
            result["service_dir"].append(service_dir.name)
        
        for dis_type in self.dis_types:
            result["dis_type"].append(dis_type.name)
            
        return result
    
    def add_missing_dis_types(self, dis_types):
        """ add a missing dis type """
        for dis_t in dis_types:
            if dis_t not in self.dis_types:
                self.dis_types.append(DistributionType.create_distribution_type(dis_t))
    
    def update(self, session, file_dict):
        """ update FileInfo """
        if file_dict.get('name', None):
            self.name = file_dict['name']
            
        if file_dict.get('regexpr', None):
            self.reg_expr = file_dict['regexpr']
            
        if file_dict.get('size', None):
            self.size = file_dict['size']
        
        if file_dict.get('type', None):
            self.type = file_dict['type']
        
        if file_dict.get('service_dir', None):
            new_service_dir = []
            for service_dir_name in file_dict.get('service_dir', []):
                service_d = session.query(ServiceDir).filter_by(name=service_dir_name).first()    
                new_service_dir.append(service_d)
            
            self.service_dirs = new_service_dir
        
        if file_dict.get('dis_type', None):
            # empty dis_type list
            del self.dis_types[:]
            for dis_t in file_dict.get('dis_type'):
                self.dis_types.append(DistributionType.create_distribution_type(dis_t))

class DAO(object):
    """ This is singleton """
    
    _instance = None
    _created   = False
    
    def __init__(self):
        
        if not DAO._created:
            #self.conn     = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
            self.conn = connections.DatabaseConnector('sqlite:////homespace/gaubert/mydb')
            self.metadata = None
            self.tbl_dict = {}
            # load dao info
            self._load()
            
            DAO._created = True
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DAO, cls).__new__(
                                cls, *args, **kwargs)
            
        return cls._instance
 
    def _load(self):
        """ load the RODD DAO info """
        self.conn.connect()
        
        self.metadata = self.conn.get_metadata()
        
        products_table = sqlalchemy.Table('products', self.metadata, autoload = True)
        
        self.tbl_dict['products']      =  products_table
        
        products_2_files_table = sqlalchemy.Table('products_2_fileinfo', self.metadata, \
                                                         sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                         sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                         autoload = True)
        
        fileinfo_2_distribution_table = sqlalchemy.Table('fileinfo_2_distribution', self.metadata, \
                                                         sqlalchemy.ForeignKeyConstraint(['dis_id'], ['distribution_type.dis_id']), \
                                                         sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                         autoload = True)
    
        # load service dirs table
        self.tbl_dict['service_dirs']  = sqlalchemy.Table('service_dirs', self.metadata, \
                                                          sqlalchemy.ForeignKeyConstraint(['chan_id'], ['channels.chan_id']), \
                                                          autoload= True)
        
        file_info_table = sqlalchemy.Table('file_info', self.metadata, autoload= True)
        
        distribution_type_table = sqlalchemy.Table('distribution_type', self.metadata, autoload = True)
        
        self.tbl_dict['distribution_type'] = distribution_type_table
        
        # load file_info table
        self.tbl_dict['file_info']     = file_info_table
        
        # load file_info table
        self.tbl_dict['channels']      = sqlalchemy.Table('channels', self.metadata, autoload= True)
        
        file_2_servdirs_table           = sqlalchemy.Table('file_2_servdirs', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['serv_id'], ['service_dirs.serv_id']), \
                                                     autoload = True)
        
        self.tbl_dict['file_2_servdirs'] = file_2_servdirs_table
    
        # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
        mapper(Product, self.tbl_dict['products'], properties={
        
        'file_infos'         :  relationship(FileInfo  , secondary=products_2_files_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        
        
       
        })
        
        # map distribution type table
        mapper(DistributionType, distribution_type_table)
            
        # map file_info table
        mapper(FileInfo, self.tbl_dict['file_info'], properties={
        'service_dirs'   : relationship(ServiceDir, secondary=file_2_servdirs_table, lazy='joined'),
        'dis_types'      : relationship(DistributionType, secondary=fileinfo_2_distribution_table, lazy='joined'),
        
        })
        
        # map channels table
        mapper(Channel, self.tbl_dict['channels'])
        
        # one to many relationship servicedirs -> channel
        mapper(ServiceDir, self.tbl_dict['service_dirs'], properties = {
            'channel': relationship(Channel)
        })

        

    def get_table(self, name):
        """ return table from the DAO """
        return self.tbl_dict[name]
    
    def get_session(self):
        """ return the session """
        return self.conn.get_session()
    