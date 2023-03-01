from .signature_handler import SignatureHandler

class MachineConfigDaemonErrorExtracting(SignatureHandler):
    def getTitle(self):
        return "machine-config-daemon could not extract machine-os-content"
    def process(self):
        pass