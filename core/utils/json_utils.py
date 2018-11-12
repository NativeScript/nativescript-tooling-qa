"""
Json utils.
"""
import json
import os
from errno import ENOENT


class JsonUtils(object):

    @staticmethod
    def __replace_value(json_data, k, v):
        """
        Replace value of key inside json object.
        :param json_data: json object.
        :param k: key.
        :param v: value.
        """
        for key in json_data.keys():
            if key == k:
                json_data[key] = v
            elif type(json_data[key]) is dict:
                JsonUtils.__replace_value(json_data[key], k, v)

    @staticmethod
    def read(file_path):
        """
        Read content of json file.
        :param file_path: Path to file.
        :return: Content of file as json object.
        """

        if not os.path.isfile(file_path):
            raise IOError(ENOENT, 'File not found.', file_path)

        with open(file_path) as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def replace(file_path, key, value):
        """
        Replace value of key in json file.
        :param file_path: File path.
        :param key: Key.
        :param value: Desired value.
        """
        with open(file_path, "r+") as jsonFile:
            data = json.load(jsonFile)
            JsonUtils.__replace_value(data, key, value)
            jsonFile.seek(0)
            json.dump(data, jsonFile, indent=4)
            jsonFile.truncate()
