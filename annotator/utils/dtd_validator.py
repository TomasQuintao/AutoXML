from lxml import etree
import sys

def validate_xml(dtd_file, xml_file):
    with open(dtd_file, "r", encoding="utf-8") as file:
        dtd = etree.DTD(file)
        
    xml_doc = etree.parse(xml_file)

    if dtd.validate(xml_doc):
        return (True, 'Valid')
    else:
        return (False, dtd.error_log.filter_from_errors())
        
def main(inp):
    print(validate_xml(inp[1], inp[2]))

if __name__ == "__main__":
    main(sys.argv)