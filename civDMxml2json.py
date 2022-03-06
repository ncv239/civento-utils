import xmltodict
import json
import os
import argparse

def get_var_info(varDictXml: dict) -> dict:
    '''
    predefined civento xml types'''
    data = {}
    var = varDictXml

    if var["@Datentyp"] == "LIST":
        pass

    elif var["@Datentyp"] == "CHOICE":
        var = var["Auswahlfeld"]
        if "Werteliste" in var.keys():
            data["values"] = var["Werteliste"]

    elif var["@Datentyp"] == "STRING":
        var = var["Textfeld"]

    elif var["@Datentyp"] == "BOOLEAN":
        var = var["JaNeinFeld"]

    elif var["@Datentyp"] == "INTEGER":
        var = var["Zahlenfeld"]
        if "Von" in var.keys():
            data["min"] = int(var["Von"])
        if "Bis" in var.keys():
            data["max"] = int(var["Bis"])

    elif var["@Datentyp"] == "PERSONENDATENSATZ":
        var = var["Personendatensatz"]

    if "Titel" in var.keys():
        data["title"] = var["Titel"]["@Standard"]
    if "Hilfetext" in var.keys():
        data["help"] = var["Hilfetext"]["@Standard"]
    
    return data




def traverseVars(xmlAsDict, data, verbose_level=0):
    _data = xmlAsDict
    if "Metadatenfeld" in _data.keys():  # we have simple vars here
        # check if we have one or more vars
        _var = _data["Metadatenfeld"]
        if type(_var) == list:
            for _field in _var:
                if verbose_level == 0:
                    data[_field["@Name"]] = _field["@Datentyp"]
                elif verbose_level == 1:
                    data[_field["@Name"]] = {"type": _field["@Datentyp"]}
                elif verbose_level == 2:
                    var_data = get_var_info(_field)
                    var_data["type"] = _field["@Datentyp"]
                    data[_field["@Name"]] = var_data
        else:  # we have one var
            if verbose_level == 0:
                data[_var["@Name"]] = _var["@Datentyp"]
            elif verbose_level == 1:
                data[_var["@Name"]] = {"type": _var["@Datentyp"]}
            elif verbose_level == 2:
                var_data = get_var_info(_var)
                var_data["type"] = _var["@Datentyp"]
                data[_var["@Name"]] = var_data
            

    # now process lists of vars recursively
    if "Metadatenliste" in _data.keys():  # we have simple vars here
        # check if we have one or more vars
        _lists = _data["Metadatenliste"]
        if type(_lists) == list:  # we have more than one list
            for _lst in _lists:
                if verbose_level == 0:
                    data[_lst["@Name"]] = {}
                    traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]], verbose_level=verbose_level)
                elif verbose_level == 1:
                    data[_lst["@Name"]] = {"type": "LIST", "value": {}}
                    traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]]["value"], verbose_level=verbose_level)
                elif verbose_level == 2:
                    data[_lst["@Name"]] = {"type": "LIST", "value": {}}
                    traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]]["value"], verbose_level=verbose_level)
                
        else:  # we have one var
            _lst = _lists
            if verbose_level == 0:
                data[_lst["@Name"]] = {}
                traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]], verbose_level=verbose_level)
            elif verbose_level == 1:
                data[_lst["@Name"]] = {"type": "LIST", "value": {}}
                traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]]["value"], verbose_level=verbose_level)
            elif verbose_level == 2:
                data[_lst["@Name"]] = {"type": "LIST", "value": {}}
                traverseVars(_lst["Metadatenobjekt"], data[_lst["@Name"]]["value"], verbose_level=verbose_level)
            



def createJsonDataFromCiventoXml(xml_path: str, json_path: str = None, verbose_level=0) -> str:
    with open(xml_path, 'r') as file:
        xml = file.read()

    _root = xmltodict.parse(xml)
    if "ns2:Bibliothek" in _root.keys():
        _process = _root['ns2:Bibliothek']
    else:
        _process = _root['ns3:Bibliothek']

    if "Vorgang" in _process.keys():
        _process = _process['Vorgang']
    else:
        print("Error: Cannot find node <Vorgang> in current XML")
        print("Aborting...")
        return
        
    _data = _process["Metadatendefinition"]
    data = {}

    for _table in _data:
        data[_table['Objekt']['@Name']] = {}
        xml_vars = _table['Objekt']
        traverseVars(xml_vars, data[_table['Objekt']['@Name']], verbose_level=verbose_level)


    if not json_path:
        json_path = os.path.splitext(xml_path)[0] + ".json"
    with open(json_path, 'w') as f:
        json.dump(data, f)
    return json_path




if __name__ == "__main__":
    epilog_str = r"""
    Examples:
        1) Create a json-datamodell file from a single input
        > python civDMxml2json.py path/to/civentofile.xml

        2) Create a json-datamodell file from a single input with additional information
        > python civDMxml2json.py -v 2 path/to/civentofile.xml

        3) Create a json-datamodell file for each of two inputs
        > python civDMxml2json.py path/to/civentofile1.xml path/to/civentofile2.xml

        4) Create a json-datamodell file for all xml-files in given directory
        > python civDMxml2json.py path/to/*.xml

    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
        description="Create a JSON file with overview of the data-modell from civento XML process export file.",
        epilog=epilog_str)
    parser.add_argument('xml_path', nargs="+", help='path for xml file(-s)')
    parser.add_argument('-v', "--verbose", default=0, type=int, choices=[0, 1, 2], help="[Default=0];\nVerbosity level:\n\t0 - very short\n\t1 - short\n\t2 - long;")
    parser.add_argument('-o', help="[Optional] Output filename. Can be used only for a single file input")
    args = parser.parse_args()

    if args.o and len(args.xml_path) > 1:
        print(args)
        raise ValueError("Cannot process multiple files with an -o argument")
    
    for fname in args.xml_path:
        print(f"Processing file {fname}")
        json_path = createJsonDataFromCiventoXml(fname, args.o, args.verbose)
        if json_path:
            print(f"Success: file created {json_path}")