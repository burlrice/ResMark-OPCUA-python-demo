from lxml import etree

class Message:
    counts = []
    variables = []
    
    def __init__(self, xml: str = None):
        self.document = etree.fromstring(xml, etree.XMLParser(recover=True))
        self.dataSet = self.document.xpath('//ProductObject//Variables//DataSet//ColumnValues//Column')

        for i in self.document.xpath('.//FieldObject'):
            xsiType = i.attrib.get('xsi:type')

            if xsiType == 'CountFieldObject':
                self.counts.append(etree.tostring(i).decode())
            elif xsiType == 'VarFieldObject':
                self.variables.append(etree.tostring(i).decode())
                
    def __str__(self):
        if self.document:
            return etree.tostring(self.document, pretty_print=True, xml_declaration=True).decode()
        
        return ''