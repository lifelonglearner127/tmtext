import codecs
import csv
import json


def convert_json_to_csv(filepath, logger=None):
    """ Receives path to .JL file (without trailing .jl) """
    json_filepath = filepath + '.jl'
    if logger is not None:
        logger.info("Convert %s to .csv", json_filepath)
    field_names = set()
    items = []
    with codecs.open(json_filepath, "r", "utf-8") as jsonfile:
        for line in jsonfile:
            item = json.loads(line.strip())
            items.append(item)
            fields = [name for name, val in item.items()]
            field_names = field_names | set(fields)

    csv.register_dialect(
        'json',
        delimiter=',',
        doublequote=True,
        quoting=csv.QUOTE_ALL)

    csv_filepath = filepath + '.csv'

    with open(csv_filepath, "w") as csv_out_file:
        csv_out_file.write(codecs.BOM_UTF8)
        writer = csv.writer(csv_out_file, 'json')
        writer.writerow(list(field_names))
        for item in items:
            vals = []
            for name in field_names:
                val = item.get(name, '')
                if name == 'description':
                    val = val.replace("\n", '\\n')
                if type(val) == type(unicode("")):
                    val = val.encode('utf-8')
                vals.append(val)
            writer.writerow(vals)
    return csv_filepath