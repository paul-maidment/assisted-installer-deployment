import importlib
import inspect
import pkgutil
import signature_handlers

class SignatureHandlerRunner:
    

    def __init__(self):
        self._plugin_namespace = signature_handlers.__name__
        self._signature_handlers = []
        handlers_to_load = self.getSignatureHandlerNames()
        print(handlers_to_load)
        if handlers_to_load != []:
            for handler_to_load in handlers_to_load:  
                self._signature_handlers.append(self.loadInstance(handler_to_load))

    def getSignatureHandlerNames(self):
        handlerNames = []
        module = importlib.import_module('signature_handlers')
        for name, obj in inspect.getmembers(module):
            print(name)
            if type(obj) is type(module) and name != "signature_handler":
                print(name)
                handlerNames = handlerNames.append(name)
        return handlerNames

    # def getSignatureHandlerNames(self):
    #     names = []
    #     name: importlib.import_module('signature_handlers')
    #     for _, name, _ in pkgutil.iter_modules(signature_handlers.__path__, self._plugin_namespace + "."):
    #         if name != signature_handlers.__name__+'._init_' and name != self._plugin_namespace+'.signature_handler':
    #             names.append(name.replace(self._plugin_namespace + ".", ""))
    #     return names

    def loadInstance(self, name):
        className = "".join(map(str.title, name.split('_')))
        module = importlib.import_module("signature_handlers." + name)
        classz = getattr(module, className) 
        return classz()

    def run(self):
        print("Running signature handlers")

        for signature_handler in self._signature_handlers:
            print(signature_handler.getTitle())
            signature_handler.process()

if __name__ == "__main__":
    SignatureHandlerRunner().run()
