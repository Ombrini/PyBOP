import importlib.util
import pybop.plot

def get_class(class_name):
    err_msg = f"Plotting backend {pybop.plot.backend} is not available."
    try:
        module = importlib.import_module('pybop.plot.' + pybop.plot.backend)
        if hasattr(module, class_name):
            return getattr(module, class_name)

        else:
            err_msg = f"Plotting backend {pybop.plot.backend} has no attribute {class_name}."
            raise ModuleNotFoundError(err_msg)
        
    except ModuleNotFoundError as error:
        # Raise an ModuleNotFoundError if the module or attribute is not available
        raise ModuleNotFoundError(err_msg) from error

def set_backend(backend):
    err_msg = f"Plotting backend {backend} is not available. The default backend has not been updated. \n"\
        f"The default backend is set to {pybop.plot.backend}"
    try:
        importlib.import_module('pybop.plot.' + backend)
        pybop.plot.backend = backend
        for attr in ['StandardPlot', 'StandardSubplot']:
            setattr(pybop.plot, attr, get_class(attr))

    except ModuleNotFoundError as error:
            # Raise an ModuleNotFoundError if the module or attribute is not available
            raise ModuleNotFoundError(err_msg) from error
    

def call_plotting_function(function_name, backend, **kwargs):
    if backend is None:
         backend = pybop.plot.backend
    err_msg = f"Plotting backend {backend} is not available."
    try:
        module = importlib.import_module('pybop.plot.' + backend)
        if hasattr(module, function_name):
            plotting_function = getattr(module, function_name)
            # Return the imported attribute
            return plotting_function(**kwargs)
        else:
            err_msg = f"Plotting backend {backend} has no attribute {function_name}."
            raise ModuleNotFoundError(err_msg)
        
    except ModuleNotFoundError as error:
        # Raise an ModuleNotFoundError if the module or attribute is not available
        raise ModuleNotFoundError(err_msg) from error
    
