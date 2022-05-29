import os
import json


def read_json(filename):
    # 'file_node' has the file name without extension so that the 'confs' variable will access its data with its name.
    # For example, if the filname is 'topology-single.json',
    # its data will be accessed as: confs.get('topology-single') OR confs['topology-single']

    file_node = filename.replace('.json', '')

    # Read The file's data
    with open(f'{files_dir}/{filename}', mode='r') as json_file:
        try:
            # return a dictionary with file_node as the key and the file data as the value
            return {file_node: json.load(json_file)}
        except json.decoder.JSONDecodeError:
            # If failed to read the file, return empty values for the file_node
            return {file_node: {}}


if __name__ == '__main__':
    files_dir = 'topology-nodes/sample'
    # This is the directory name where the json files exists.
    # Read out all the files from the 'files_dir' and get only the files having '.json' extension
    json_files = [filename for filename in os.listdir(files_dir) if filename.endswith('.json')]

    # A dictionary of objects that will store all the data from the json files and the data could be accessed
    # with the filename node without its extension. For example: confs.get('topology-single') OR confs['topology-single']
    confs = {}

    # Iterate over all the json files to insert the data into the 'confs' dictionary.
    for json_filename in json_files:
        json_data = read_json(json_filename)
        confs.update(json_data)


    # Now you can access any file node or file's data node with this 'confs' variable anywhere in this python file.
    # For example, to access the 'topology-single.json' file node data, you can do confs.get('topology-single')
    # To access the data nodes from topology-single file, you can do as: confs.get('topology-single').get('title')
    # And so on you can access any file_node and data nodes
    # confs.get('deployment-1').get('nodesUsedForCorfuInstance')[0]
