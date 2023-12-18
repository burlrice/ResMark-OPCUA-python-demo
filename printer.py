from opcua import Client, ua

class Printer:
    class OPCUA:
        Port = 16664
        ObjectId = "i=85"
        Namespace = "ns=2"
        
    def __init__(self, ipaddr):
        self.client = Client("opc.tcp://{}:{}".format(ipaddr, self.OPCUA.Port), timeout=20)
        self.client.connect()
        
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
