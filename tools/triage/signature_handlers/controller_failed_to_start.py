from .signature_handler import SignatureHandler

class ControllerFailedToStart(SignatureHandler):
    def getTitle(self):
        return "Assisted Installer Controller failed to start"
    def process(self):
        pass