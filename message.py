from lxml import etree

class Message:
    name = ''
    
    def __init__(self, name: str, xml: str):
        self.name = name
        self.counts = []
        self.variables = []
        self.dataSet = {}
        
        self.document = etree.fromstring(xml, etree.XMLParser(recover=True))

        for i in self.document.xpath('//ProductObject//Variables//DataSet//ColumnValues//Column'):
            self.dataSet[i.attrib.get('Name')] = i.attrib.get('Value')

        for i in self.document.xpath('.//FieldObject'):
            xsiType = i.attrib.get('xsi:type')

            if xsiType == 'CountFieldObject':
                self.counts.append(i.attrib.get('StartCount'))
            elif xsiType == 'VarFieldObject':
                # TODO self.variables.append(etree.tostring(i).decode().strip())
                print('TODO')
                
    def __str__(self):
        if self.document:
            return etree.tostring(self.document, pretty_print=True, xml_declaration=True).decode()
        
        return ''
    
    def hasVariables(self):
        return (len(self.counts) + len(self.variables) + len(self.dataSet)) > 0