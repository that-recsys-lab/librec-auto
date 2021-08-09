# this file will be where we create our own errors
from librec_auto.core.util.utils import force_list
import logging
from abc import abstractmethod

# some rudimentary errors:
#     FileNotFound: raise when the user's provided files (data, scripts, etc.) aren't found
#     InvalidConfiguration: raise when there's an error in the configuration file that will prevent librec from running as it should
#         if the user has rerank and bbo
#         if the user has value tags with bbo
#         if the user is using incorrect metrics
#     LibRecError: raise when an error occurs on Java LibRec side. 
#     ScriptFailError: raise when a script results in an error
#     JavaError: 
        # raise when Java not installed
        # raise when version is incompatible

class LibRecAutoException(Exception):
    """Exceptions raised during the compilation of LibRec-Auto

    Attributes:
        element_name -- element which caused the error
        message -- explanation of the error
    """
    def __init__(self, elem_name, message="LibRec-Auto Exception."):
        self.element_name = elem_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.element_name} -> {self.message}'

class InvalidConfiguration(LibRecAutoException):
    """Exception raised for errors in the configuration file XML.
    """
    # may want to make it less broad, go into more detail
    def __init__(self, elem_name, message="Error processing configuration file."):
        super().__init__(elem_name, message)
        self._write_to_log()

    def _write_to_log(self):
        logging.error(f' Configuration file: {self.element_name}: {self.message}')

class UnknownConfigurationElementException(InvalidConfiguration):
    """Exception raised for unknown elements in the configutation file.
    """
    def __init__(self, elem_name, message="Unknown element in configuration file"):
        super().__init__(elem_name, message)
        self._write_to_log()

class InvalidCommand(LibRecAutoException):
    """Exception raised when the user gives a command without supplying the 
    necessary scripts.
    """
    def __init__(self, elem_name, message="Command not applicable."):
        super().__init__(elem_name, message)
        self._write_to_log()

    def _write_to_log(self):
        logging.error(f' Command Line: {self.element_name}: {self.message}')
        
class LibRecError(LibRecAutoException):
    """Exception raised for errors in LibRec.
    """
    def __init__(self, elem_name, message="Error from LibRec"):
        super().__init__(elem_name, message)

class ScriptFailureException(LibRecAutoException):
    """Exception raised when scripts fail to load or run.
    """
    def __init__(self, elem_name, message="Script failed to complete", errors=None):
        super().__init__(elem_name, message)
        self._script_errors = errors
        self._write_to_log()
    
    def _write_to_log(self):
        if type(self._script_errors) == str:
            logging.error(f' Script failure: {self.element_name}: {self.message}\n{self._script_errors}')
        elif type(self._script_errors) == list:
            for error in self._script_errors:
                logging.error(f' Script failure: {self.element_name}: {self.message}\n{error}')
        else: logging.error(f' Script failure: {self.element_name}: {self.message}')


class JavaVersionException(LibRecAutoException):
    """Exception raised when the user's Java version is incompatible with LibRec.
    """
    def __init__(self, elem_name, message="Java version incompatible with LibRec, please update."):
        super().__init__(elem_name, message)
        self._write_to_log()

    def _write_to_log(self):
        logging.error(f' Java Version: {self.element_name}: {self.message}')

class UnsupportedFeatureException(LibRecAutoException):
    """Exception raised for features we have not impolemented yet.
    """
    def __init__(self, elem_name, message=""):
        super().__init__(elem_name, message)
        self._write_to_log()

    def _write_to_log(self):
        logging.error(f' Unsupported feature: {self.element_name}: {self.message}')