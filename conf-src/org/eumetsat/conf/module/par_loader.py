'''
Created on Feb 1, 2010

@author: guillaume.aubert@ctbto.org
'''

import re
import os
import org.ctbto.conf.resource as resource

class ParError(Exception):
    """Base class for ConfigParser exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__
    
class SubstitutionError(ParError):
    """Base class for substitution-related exceptions."""

    def __init__(self, lineno, location, msg):
        ParError.__init__(self, 'SubstitutionError on line %d: %s. %s' % (lineno, location, msg) if lineno != - 1 else 'SubstitutionError in %s. %s' % (lineno, location))
        

class ParsingError(ParError):
    """Raised when a configuration file does not follow legal syntax."""
    def __init__(self, filename):
        ParError.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []

    def append(self, lineno, line):
        """ add error message """
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)
        
    def get_error(self):
        """ return the error """
        return self
    
class ParReader(object):
    """ 
        Class reading a par file (ctbto conf files).
        Not all functionalities of the par files are supported.
        Supported functionalities
        - param = values
        - includes: par=/tmp/t.par
        - variables: t=$(var)/rest
    """
    
    _OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )
    
    #higher than in a normal conf system because par is messy
    MAX_INCLUDE_DEPTH = 20
    
    # very permissive regex
    _VARIABLERE = re.compile(r"\$\((?P<envvar>\w*)\)")
    
    def __init__(self):
        """ constructor """
        
        # list of sections
        self._section = {}
        
        self._file_path = None
    
    def _read_include(self, a_original_file, lineno, include_file, depth):
        """ read an included par file """
        # Error if depth is MAX_INCLUDE_DEPTH 
        if depth >= ParReader.MAX_INCLUDE_DEPTH:
            raise ParsingError("Cannot do more than %d nested includes. It is probably a mistake as you might have created a loop of includes." % (ParReader.MAX_INCLUDE_DEPTH))
        
        if not os.path.exists(include_file):
            raise ParsingError("Include PAR file %s declared lineno %d of %s doesn't exist." % (include_file, lineno, a_original_file))
    
        # add include file and populate the section hash
        return self.read(include_file, depth + 1)

    def _replace_vars(self, a_str, location, lineno= - 1):
        """ replace variables """
    
        toparse = a_str
    
        index = toparse.find("$(")
    
        # if found opening %( look for end bracket)
        if index >= 0:
            # look for closing brackets while counting openings one
            closing_brack_index = self._get_closing_bracket_index(index, a_str, location, lineno)
        
            #print "closing bracket %d"%(closing_brack_index)
            var = toparse[index:closing_brack_index + 1]
            
            #result of the lookup below
            lookup_result = None
            
            m = ParReader._VARIABLERE.match(var)
        
            if m == None:
                raise SubstitutionError(lineno, location, "Cannot find the proper syntax structure for a variable ( $(VAR) ) but found an opening bracket (. Malformated expression %s" % (var))
            else:
            
                # recursive calls
                #var = _replace_vars(m.group('envvar'), location, - 1)
                var = m.group('envvar')
                    
                #lookup process
                
                #first look in command line
                r = resource.Resource(CliArgument=var, EnvVariable=None)
                
                lookup_result = r.getValue(False)
                
                # second, look in Shell ENV
                r = resource.Resource(CliArgument=None, EnvVariable=var)
                
                dummy = r.getValue(False)
                if dummy:
                    lookup_result = dummy
            
                # third look in conf file
                dummy = self._section.get(var.lower(), None)
                if dummy:
                    lookup_result = dummy
                
            #replace the found var with the substitution
            toparse = toparse.replace('$(%s)' % (var), lookup_result)
            
            #replace the 
            return self._replace_vars(toparse, location, - 1)    
        else:   
            return toparse 


    def _get_closing_bracket_index(self, index, s, location, lineno):
        """ private method used by _replace_vars to count the closing brackets.
            
            Args:
               index. The index from where to look for a closing bracket
               s. The string to parse
               group. group and options that are substituted. Mainly used to create a nice exception message
               option. option that is substituted. Mainly used to create a nice exception message
               
            Returns: the index of the found closing bracket
        
            Raises:
               exception NoSectionError if the section cannot be found
        """
        
        tolook = s[index + 2:]
   
        opening_brack = 1
        closing_brack_index = index + 2
    
        i = 0
        for _ch in tolook:
            if _ch == ')':
                if opening_brack == 1:
                    return closing_brack_index
                else:
                    opening_brack -= 1
     
            elif _ch == '(':
                if tolook[i - 1] == '$':
                    opening_brack += 1
        
            # inc index
            closing_brack_index += 1
            i += 1
    
        raise SubstitutionError(lineno, location, "Missing a closing bracket in %s" % (tolook))
    
    def read(self, a_path, a_depth = 0):
        ''' read a par file '''
        
        lineno = 0
        err    = None
       
        the_fp = open(a_path) 
        
        self._file_path = a_path
        
        while True:
            line = the_fp.readline()
            if not line:
                break
            lineno = lineno + 1
            
            # to be changed include in this form %include
            if line.startswith('%include'):
                #self._read_include(lineno, line, fpname, depth)
                continue
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            else:
                the_match = ParReader._OPTCRE.match(line)
                if the_match:
                    optname, vi, optval = the_match.group('option', 'vi', 'value')
                    if vi in ('=', ':') and ';' in optval:
                        # ';' is a comment delimiter only if it follows
                        # a spacing character
                        pos = optval.find(';')
                        if pos != - 1 and optval[pos - 1].isspace():
                            optval = optval[:pos]
                    optval = optval.strip()
                    # allow empty values
                    if optval == '""':
                        optval = ''
                    
                    optname = optname.rstrip().lower()
                    
                    # replace variables if necessary
                    optval = self._replace_vars(optval, line, lineno)
                    
                    # if optname = par then it is an include
                    if optname == 'par':
                        self._read_include(a_path, lineno, optval, a_depth)
                        
                    self._section[optname] = optval
                else:
                    # a non-fatal parsing error occurred.  set up the
                    # exception but keep going. the exception will be
                    # raised at the end of the file and will contain a
                    # list of all bogus lines
                    if not err:
                        err = ParsingError(a_path)
                    err.append(lineno, repr(line))
        
        the_fp.close()   
                         
        return self._section
        

def read(a_path):
    """ generic function that each conf module needs to have """
    
    par_reader = ParReader()
    
    return par_reader.read(a_path)
    