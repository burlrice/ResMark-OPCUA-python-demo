from pickletools import uint8
import zlib
import re

from enum import Enum
from opcua import Client, ua

from Dialogs.path import resolveMessage

class Printer:
    class Errors:
        MISSING_CARTRIDGE = "No ink cartridge inserted"
        INK_LOW = "Ink is Low"
        WASTE_FULL = "Waste is full"
        INK_OUT = "Print head Ink Out"        
        warnings = [INK_LOW]
        errors = [MISSING_CARTRIDGE, WASTE_FULL, INK_OUT]
        
    class OPCUA:
        Port = 16664
        ObjectId = "i=85"
        Namespace = "ns=2"
        
    class State(Enum):
        Ok = 1
        Warning = 2
        Error = 3
        
    errors = {}
    
    def __init__(self, ipaddr: str):
        self.client = Client("opc.tcp://{}:{}".format(ipaddr, self.OPCUA.Port), timeout=20)
        self.client.connect()        
        self.name = self.callMethod('GetBroadcastingSsid')[0]
        
    def __del__(self):
        self.client.disconnect()

    def callMethod(self, methodName: str, *args):
        method = self.client.get_node("{};s={}".format(self.OPCUA.Namespace, methodName))
        node = self.client.get_node(self.OPCUA.ObjectId)
        
        if (len(args) == 0):
            return node.call_method(method)
        else:
            return node.call_method(method, *args)
        
    def GetStatusInformation(self):
        result = self.callMethod('GetStatusInformation', ua.Variant(1, ua.VariantType.Int32))
        error = result[0]

        self.errors = {}
        
        try:
            if not error:
                for i in result[7]:
                    split = i.split(':')
                    
                    if split[0] not in self.errors:
                        self.errors[split[0]] = []
                        
                    self.errors[split[0]].append(split[2])
                    
            for i in self.errors:
                self.errors[i] = list(set(self.errors[i]))
        except:
            pass
        
        return result[1:] if len(error) == 0 else []
    
    def GetState(self) -> State:
        for i in self.errors:
            for e in self.errors[i]:
                if e in self.Errors.errors:
                    return self.State.Error
                elif e in self.Errors.warnings:
                    return self.State.Warning    
        
        return self.State.Ok;
    
    def GetStoredMessageList(self):
        result = self.callMethod('GetStoredMessageList')
        error = result[0]
        result = result[1:][0] if len(error) == 0 else []
        result = [file for file in result if not file.lower().endswith('.prd')]
        result = [re.sub(r'\.[^.]+$', '', file) for file in result]
        return result
            
    def PrintPreviewCurrentCompressed(self):
        result = self.callMethod('PrintPreviewCurrentCompressed', ua.Variant(1, ua.VariantType.Int32))
        error = result[0]

        if len(error) == 0 and result[2]:
            compressed = bytes(result[2]);
            decompressed = zlib.decompress(compressed, bufsize=result[1])    

            return decompressed
            
        return None
    
    def PathPrintStoredMessage(self, folder: str, message: str) -> bool:
        result = self.callMethod('PathPrintStoredMessage', 
                                 ua.Variant(1, ua.VariantType.Int32), 
                                 ua.Variant(folder, ua.VariantType.String), 
                                 ua.Variant(resolveMessage(message), ua.VariantType.String))
        return result == ua.StatusCodes.Good
    
    def SetMessageCount(self, count: int) -> None:
        self.callMethod('SetMessageCount', ua.Variant(max(0, count), ua.VariantType.UInt64))
        
    def StopPrinting(self) -> bool:
        result = self.callMethod('StopPrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0

    def ResumePrinting(self) -> bool:
        result = self.callMethod('ResumePrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0

    def CancelPrinting(self) -> bool:
        result = self.callMethod('CancelPrinting', ua.Variant(1, ua.VariantType.Int32))
        
        return len(result) == 0
    
    def RecallMessage(self, message: str) -> str:
        result = self.callMethod('RecallMessage', resolveMessage(message))
        error = result[0]
        return result[1] if  len(error) == 0 else None
    
    def PrintMessage(self, xml: str) -> bool:
        error = self.callMethod('PrintPrd', ua.Variant(xml, ua.VariantType.String), ua.Variant(1, ua.VariantType.Int32))

        return len(error) == 0
    
        