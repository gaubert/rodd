'''
Created on Sep 29, 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy
import decimal
import simplejson as json

from sqlalchemy.orm import mapper, relationship, backref

import eumetsat.common.logging_utils as logging
from eumetsat.db import connections
from eumetsat.common.collections import OrderedDict


class Product(object):
    """ Product Object """
    
    LOGGER = logging.LoggerFactory.get_logger("Product")
    
    def __init__(self, title, internal_id, description, disseminated, status):
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
                     self._dis_type_cache["eumetcast-info"], \
                     self._dis_type_cache["gts-info"], \
                     self._dis_type_cache["data-centre-info"], \
                     self._dis_type_cache["geonetcast-info"])
               
    def _populate_type_cache(self):
        """ separate files by distribution types """
        
        result = self._dis_type_cache     
        for finfo in self.file_infos:
            for type in finfo.dis_types:
                if type == DistributionType('EUMETCAST'):
                    # add in result distribution for the first time if necessary
                    if "eumetcast-info" not in result["distribution"]:
                        result["distribution"].append("eumetcast-info")
                
                    result["eumetcast-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('GTS'):
                    # add in result distribution for the first time if necessary
                    if "gts-info" not in result["distribution"]:
                        result["distribution"].append("gts-info")
                    
                    result["gts-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('ARCHIVE'):
                    # add in result distribution for the first time if necessary
                    if "data-centre-info" not in result["distribution"]:
                        result["distribution"].append("data-centre-info")
                    
                    result["data-centre-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('GEONETCAST'):
                    if "geonetcast-info" not in result["distribution"]:
                        result["distribution"].append("geonetcast-info")
                        
                    result["geonetcast-info"]["files"].append(finfo.jsonize())
        
        return result         
    
    def update(self, a_prod_dict, a_session):
        """ update attributes of the product. Policy is to replace all attributes with existing ones """
        
        
        if a_prod_dict.get('name', None):
            self.title = a_prod_dict['name']
            
        if a_prod_dict.get('description', None):
            self.description = a_prod_dict['description']
        
        file_dict = {}
        Product.LOGGER.info("HELLO")
        
        new_file_infos = []
        
        for a_file in a_prod_dict.get('gts-info', { 'files' : [] }).get('files', []):
    
            #look for existing file-info
            Product.LOGGER.info("HELLO 1")
            Product.LOGGER.info("a_file = %s" %(a_file))
            
            finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()    
            if not finfo:    
                #create file object
                finfo = FileInfo(  a_file["name"], \
                                   a_file.get("regexpr", ""), \
                                   a_file["size"], \
                                   a_file["type"])
                
        
                #finfo.dis_types.append(ARCHIVE_DIS_TYPE)
                diss_type = a_session.query(DistributionType).filter_by(name='GTS').first() 
                finfo.dis_types.append(diss_type)
                            
            #add in new_file_infos   
            new_file_infos.append(finfo)
            file_dict[a_file['name']] = finfo
        
        for a_file in a_prod_dict.get('eumetcast-info', { 'files' : [] }).get('files', []):    
            #look for existing file-info
            finfo = file_dict.get(a_file['name'], None)
            if not finfo:    
                finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()   
                if not finfo:          
                    #create file object
                    finfo = FileInfo(  a_file["name"], \
                                       a_file.get("regexpr", ""), \
                                       a_file["size"], \
                                       a_file["type"])
                    
            
                    #finfo.dis_types.append(ARCHIVE_DIS_TYPE)
                    diss_type = a_session.query(DistributionType).filter_by(name='EUMETCAST').first() 
                    finfo.dis_types.append(diss_type)
                            
            new_file_infos.append(finfo)
            file_dict[a_file['name']] = finfo
        
        for a_file in a_prod_dict.get('datacentre-info', { 'files' : [] }).get('files', []): 
            #look for existing file-info
            finfo = file_dict.get(a_file['name'], None)
            if not finfo:    
                finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()   
                if not finfo:          
                    #create file object
                    finfo = FileInfo(  a_file["name"], \
                                       a_file.get("regexpr", ""), \
                                       a_file["size"], \
                                       a_file["type"])
                    
            
                    #finfo.dis_types.append(ARCHIVE_DIS_TYPE)
                    diss_type = a_session.query(DistributionType).filter_by(name='ARCHIVE').first() 
                    finfo.dis_types.append(diss_type)
                            
            new_file_infos.append(finfo)
            file_dict[a_file['name']] = finfo
            
        for a_file in a_prod_dict.get('geonetcast', { 'files' : [] }).get('files', []):    
            #look for existing file-info
            finfo = file_dict.get(a_file['name'], None)
            if not finfo:    
                finfo = a_session.query(FileInfo).filter_by(name=a_file['name']).first()   
                if not finfo:          
                    #create file object
                    finfo = FileInfo(  a_file["name"], \
                                       a_file.get("regexpr", ""), \
                                       a_file["size"], \
                                       a_file["type"])
                    
            
                    #finfo.dis_types.append(ARCHIVE_DIS_TYPE)
                    diss_type = a_session.query(DistributionType).filter_by(name='GEONETCAST').first() 
                    finfo.dis_types.append(diss_type)
                            
            new_file_infos.append(finfo)
            file_dict[a_file['name']] = finfo
        
        # Replace the current file_info with new_file_info if not empty
        self.file_infos = new_file_infos
    
    def add_files(self):
        pass
    
    def get_index(self, a_force):
        
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
        return self.get_index().get(name,None)
        
        
    def jsonize(self):
        
        result = OrderedDict()
        
        result["name"]         = self.title 
        result["uid"]          = self.internal_id
        result["description"]  = self.description
        result["distribution"] = []
        
        
        result["eumetcast-info"]   = { "files": [] }
        result["gts-info"]         = { "files": [] }
        result["data-centre-info"] = { "files": [] }
        result["geonetcast-info"]  = { "files": [] }
        
        for finfo in self.file_infos:
            for type in finfo.dis_types:
                if type == DistributionType('EUMETCAST'):
                    # add in result distribution for the first time if necessary
                    if "eumetcast-info" not in result["distribution"]:
                        result["distribution"].append("eumetcast-info")
                
                    result["eumetcast-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('GTS'):
                    # add in result distribution for the first time if necessary
                    if "gts-info" not in result["distribution"]:
                        result["distribution"].append("gts-info")
                    
                    result["gts-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('ARCHIVE'):
                    # add in result distribution for the first time if necessary
                    if "data-centre-info" not in result["distribution"]:
                        result["distribution"].append("data-centre-info")
                    
                    result["data-centre-info"]["files"].append(finfo.jsonize())
                elif type == DistributionType('GEONETCAST'):
                    if "geonetcast-info" not in result["distribution"]:
                        result["distribution"].append("geonetcast-info")
                        
                    result["geonetcast-info"]["files"].append(finfo.jsonize())
            
        return result
        
class ServiceDir(object):
    """ServiceDir object """
    def __init__(self, name, channel):
        self.serv_id     = None
        self.name        = name
        self.channel     = channel
    
    def __repr__(self):
        return "<ServiceDir(%s'%s', '%s')>" % ( (("'serv_id:%s', " % (self.serv_id)) if self.serv_id else ""),\
                                                self.name, \
                                                self.channel)
    
    def jsonize(self):
        """ jsonize """
        result = {}
        
        result['name']    = self.name
        result['channel'] = self.channel.name if self.channel else "" 
        
        return result
    
class DistributionType(object):
    """ DistributionType object """
    def __init__(self, name):
        self.dis_id   = None
        self.name     = name
    
    def __repr__(self):
        return "<DistributionType('%s')>" % (self.name)
    
    def __eq__(self, ext_obj):
        """ equality operator """
        return (ext_obj.name == self.name)
    
    @classmethod
    def translate_name(self, a_type):
        
        if a_type == 'EUMETCAST':
            return 'eumetcast-info'
        elif a_type == 'GTS':
            return 'gts-info'
        elif a_type == 'GEONETCAST':
            return 'geonetcast-info'
        elif a_type == 'ARCHIVE':
            return 'data-centre-info'
        else:
            return 'unknown-distribution'
        
        
    def jsonize(self):
        """ jsonize """
        
        #result = { 'name' : self.name }
        return DistributionType.translate_name(self.name)
        
    
class Channel(object):
    """ Channel object """
    
    def __init__(self, name, address, min_rate, max_rate, channel_function):
        """ constructor """
        self.chan_id           = None
        self.name              = name
        self.multicast_address = address
        self.min_rate          = min_rate
        self.max_rate          = max_rate
        self.channel_function  = channel_function
        
    def __repr__(self):
        return "<Channel(%s'%s', '%s', '%s', '%s', '%s')>" % ( (( "'chan_id:%s', " % (self.chan_id)) if self.chan_id else ""),\
                                                              self.name, self.multicast_address, self.min_rate, self.max_rate, self.channel_function)
    
    def jsonize(self):
        """ jsonize """
        result = {}
        
        result['name']              = self.name
        result['multicast_address'] = self.multicast_address
        
        # given as decimal by sqlalchemy to ROUND_UP to get only integer values 
        result['min_rate']            = str(decimal.Decimal(self.min_rate).quantize(decimal.Decimal('1')))
        result['max_rate']            = str(decimal.Decimal(self.max_rate).quantize(decimal.Decimal('1')))
        
        result['channel_function']    = self.channel_function
        
        return result
        

class FileInfo(object):
    """ FileInfo object """
    
    LOGGER = logging.LoggerFactory.get_logger("FileInfo")
    
    def __init__(self, name, reg_expr, size, type):
         
        self.file_id       = None
        self.name          = name
        self.reg_expr      = reg_expr
        self.size          = size
        self.type          = type
        self.service_dirs  = []
        self.dis_types     = []
    
    def __repr__(self):
        return "<FileInfo(%s'%s','%s', '%s', '%s', '%s')>" % ((( "'file_id:%s', " % (self.file_id)) if self.file_id else ""), self.name, self.reg_expr, self.size, self.type, self.service_dirs)

    def jsonize(self):
        
        result = {"service_dir" : []}
        
        result["name"]        = self.name
        result["regexpr"]     = self.reg_expr
        result["size"]        = self.size
        result["type"]        = self.type
        
        for service_dir in self.service_dirs:
            result["service_dir"].append(service_dir.name)
            
        return result
    
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
            for service_dir_name in file_dict.get('service_dir',[]):
                service_d = session.query(ServiceDir).filter_by(name=service_dir_name).first()    
                new_service_dir.append(service_d)
            
            self.service_dirs = new_service_dir
        

class DAO(object):
    """ This is singleton """
    
    _instance = None
    _created   = False
    
    def __init__(self):
        
        if not DAO._created:
            self.conn     = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
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
        """ load the RODDDAO info """
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
        
        
        #create many to many relation table
        # beware add foreign key constraints manually as they do not exist in MYSQL
        products_2_eumetcast_table      = sqlalchemy.Table('products_2_eumetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_eumetcast'] = products_2_eumetcast_table
        
        products_2_geonetcast_table     = sqlalchemy.Table('products_2_geonetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_geonetcast'] = products_2_geonetcast_table
        
        products_2_gts_table            = sqlalchemy.Table('products_2_gts', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_gts'] = products_2_gts_table
        
        products_2_data_centre_table    = sqlalchemy.Table('products_2_data_centre', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_data_centre'] = products_2_data_centre_table
        
        file_2_servdirs_table           = sqlalchemy.Table('file_2_servdirs', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['serv_id'], ['service_dirs.serv_id']), \
                                                     autoload = True)
        
        self.tbl_dict['file_2_servdirs'] = file_2_servdirs_table
    
        # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
        mapper(Product, self.tbl_dict['products'], properties={
        'data_centre_infos'  :  relationship(FileInfo,   secondary=products_2_data_centre_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'gts_infos'          :  relationship(FileInfo,   secondary=products_2_gts_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'eumetcast_infos'    :  relationship(FileInfo  , secondary=products_2_eumetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'geonetcast_infos'   :  relationship(FileInfo  , secondary=products_2_geonetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        
        'file_infos'         :  relationship(FileInfo  , secondary=products_2_files_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        
        
       
        })
        
        # map distribution type table
        mapper(DistributionType, distribution_type_table)
            
        # map file_info table
        mapper(FileInfo, self.tbl_dict['file_info'], properties={
        'service_dirs'   : relationship(ServiceDir, secondary=file_2_servdirs_table),
        'dis_types'      : relationship(DistributionType, secondary=fileinfo_2_distribution_table),
        
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
    