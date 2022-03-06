# civento-utils
civento utilities to speed up routine tasks


## Installation
```bash
git clone https://github.com/ncv239/civento-utils.git
cd civento-utils
pip install -r requirements.txt
```

![installation gif](https://github.com/ncv239/civento-utils/blob/main/img/install.gif)

# civDMxml2json

This tool generates a human-readable json file with datamodell of civento process exported as xml file

## Usage

> You can use the `--help` option to get more details about the commands and their options
```bash
python civDMxml2json.py --help
```

> Basic usage
```bash
python civDMxml2json.py civentofile.xml
```

> Basic usage (create a json file for a simple file)
```bash
python civDMxml2json.py civentofile.xml
```

> Advanced usage (create multiple json files from all xml files in given dir with more details)
```bash
python civDMxml2json.py -v 2 path/to/xmlfiles/*.xml
```

![usage gif](https://github.com/ncv239/civento-utils/blob/main/img/usage_civDMxml2json.gif)