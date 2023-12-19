import zlib
from opcua import Client, ua

class Printer:
    class OPCUA:
        Port = 16664
        ObjectId = "i=85"
        Namespace = "ns=2"
        
    def __init__(self, ipaddr):
        self.client = Client("opc.tcp://{}:{}".format(ipaddr, self.OPCUA.Port), timeout=20)
        self.client.connect()        
        self.name = self.callMethod('GetBroadcastingSsid')[0]
        
    def __del__(self):
        self.client.disconnect()

    def callMethod(self, methodName, *args):
        method = self.client.get_node("{};s={}".format(self.OPCUA.Namespace, methodName))
        node = self.client.get_node(self.OPCUA.ObjectId)
        
        if (len(args) == 0):
            return node.call_method(method)
        else:
            return node.call_method(method, *args)
        
    def GetStatusInformation(self):
        result = self.callMethod('GetStatusInformation', ua.Variant(1, ua.VariantType.Int32))
        error = result[0]
        return result[1:] if len(error) == 0 else []
    
    def GetStoredMessageList(self):
        result = self.callMethod('GetStoredMessageList')
        error = result[0]
        return result[1:][0] if len(error) == 0 else []
            
    def PrintPreviewCurrentCompressed(self):
        result = self.callMethod('PrintPreviewCurrentCompressed', ua.Variant(1, ua.VariantType.Int32))
        error = result[0]

        if len(error) == 0 and result[2]:
            compressed = bytes(result[2]);
            decompressed = zlib.decompress(compressed, bufsize=result[1])    

            return decompressed
            
        return None
    
    def PathPrintStoredMessage(self, folder, message) -> bool:
        result = self.callMethod('PathPrintStoredMessage', 
                                 ua.Variant(1, ua.VariantType.Int32), 
                                 ua.Variant(folder, ua.VariantType.String), 
                                 ua.Variant(message, ua.VariantType.String))
        return result == ua.StatusCodes.Good

    def StopPrinting(self) -> bool:
        result = self.callMethod('StopPrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0

    def ResumePrinting(self) -> bool:
        result = self.callMethod('ResumePrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0

    def CancelPrinting(self) -> bool:
        result = self.callMethod('CancelPrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0
        