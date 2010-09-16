'''
Created on Feb 3, 2010

@author: guillaume.aubert@eumetsat.int

common package to regroup conf exceptions

'''

# exception classes
class Error(Exception):
    """Base class for Conf exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__
    
class NoOptionError(Error):
    """A requested option was not found."""

    def __init__(self, option, section):
        Error.__init__(self, "No option %r in section: %r" % 
                       (option, section))
        self.option = option
        self.section = section

class NoSectionError(Error):
    """Raised when no section matches a requested option."""

    def __init__(self, section):
        Error.__init__(self, 'No section: %r' % (section,))
        self.section = section

class SubstitutionError(Error):
    """Base class for substitution-related exceptions."""

    def __init__(self, lineno, location, msg):
        Error.__init__(self, 'SubstitutionError on line %d: %s. %s' % (lineno, location, msg) if lineno != - 1 else 'SubstitutionError in %s. %s' % (lineno, location))
        
class IncludeError(Error):
    """ Raised when an include command is incorrect """
    
    def __init__(self, msg, origin):
        Error.__init__(self, msg)
        self.origin = origin
        self.errors = []


class ParsingError(Error):
    """Raised when a configuration file does not follow legal syntax."""
    def __init__(self, filename):
        Error.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []

    def append(self, lineno, line):
        """ add error message """
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)
        
    def get_error(self):
        """ return the error """
        return self
        
class MissingSectionHeaderError(ParsingError):
    """Raised when a key-value pair is found before any section header."""

    def __init__(self, filename, lineno, line):
        ParsingError.__init__(
            self,
            'File contains no section headers.\nfile: %s, line: %d\n%r' % 
            (filename, lineno, line))
        self.filename = filename
        self.lineno = lineno
        self.line = line