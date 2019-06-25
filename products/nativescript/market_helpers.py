import json
import os
import urllib

from core.log.log import Log
from core.settings import Settings


class FlavorStatus(object):
    def __init__(self):
        self.android = None
        self.ios = None
        self.slow = None

    def set_android(self, value):
        self.android = value

    def get_android(self):
        return self.android

    def set_ios(self, value):
        self.ios = value

    def get_ios(self):
        return self.ios

    def set_slow(self, value):
        self.slow = value

    def get_slow(self):
        return self.slow


class Market(object):

    @staticmethod
    def get_data_github():
        url = "https://raw.githubusercontent.com/NativeScript/code-samples/master/data/all.json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        samples = data['samples']
        testing_data = []
        for sample in samples:
            control_string = ""
            samplename = sample['name']
            sample_name = samplename.replace(" ", "_")
            flavors = sample['links']
            for key in flavors:
                record = []
                sample_url = str(flavors[key]).strip()
                if sample_url:
                    record.append(sample_name)
                    record.append(sample_url)
                    record.append(control_string)
                    record.append(key)
                    testing_data.append(record)

        return testing_data

    @staticmethod
    def get_data_market():
        url = "https://market.nativescript.org/api/samples?take=1000"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        samples = data['data']
        testing_data = []
        for sample in samples:
            control_string = ""
            samplename = sample['name']
            sample_name = samplename.replace(" ", "_")
            flavors = sample['links']
            for key in flavors:
                record = []
                sample_url = str(flavors[key]).strip()
                if sample_url:
                    record.append(sample_name.encode("utf8"))
                    record.append(sample_url)
                    record.append(control_string)
                    record.append(key.encode("utf8"))
                    testing_data.append(record)

        return sorted(testing_data, key=lambda smpl: smpl[0])

    @staticmethod
    def get_preserved_data():
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.json')
        data = None
        if os.path.isfile(file_path):
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
        else:
            with open(file_path, "w") as new_file:
                Log.info("Results.json file created " + new_file.name)

        return data

    @staticmethod
    def serialize(obj):
        return obj.__dict__

    @staticmethod
    def preserve_data(record):
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.json')
        preserved_data = Market.get_preserved_data()
        temp_sample_status = None
        record_name = record["name"]
        original_index = None

        if preserved_data:
            temp_sample_status = next((x for x in preserved_data if x["name"] == record_name), None)
            if temp_sample_status is not None:
                original_index = preserved_data.index(temp_sample_status)
        else:
            preserved_data = []

        if temp_sample_status is None:
            temp_sample_status = {
                "name": record_name,
                "core": None,
                "angular": None,
                "vue": None
            }

        if record["flavor"] == "core":
            temp_sample_status["core"] = Market.serialize(Market.get_flavor_status(record))

        if record["flavor"] == "angular":
            temp_sample_status["angular"] = Market.serialize(Market.get_flavor_status(record))

        if record["flavor"] == "vue":
            temp_sample_status["vue"] = Market.serialize(Market.get_flavor_status(record))

        if original_index is None:
            preserved_data.append(temp_sample_status)
        else:
            preserved_data[original_index] = temp_sample_status

        with open(file_path, "w") as json_file:
            json.dump(preserved_data, json_file, indent=4)

        Log.info("++++============DATA==============++++")
        Log.info(record["name"])
        Log.info("Android Pass: " + record["android"])
        Log.info("iOS Pass: " + record["ios"])
        Log.info("++++============END==============++++")

    @staticmethod
    def get_flavor_status(record):
        temp_flavor_status = FlavorStatus()
        temp_flavor_status.set_android(Market.convert_to_bool(record["android"]))
        temp_flavor_status.set_ios(Market.convert_to_bool(record["ios"]))
        temp_flavor_status.set_slow(Market.convert_to_bool(record["slow"]))

        return temp_flavor_status

    @staticmethod
    def convert_to_bool(value):
        return value.lower() in ("yes", "true", "t", "1")

    @staticmethod
    def remove_results_file():
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.json')
        if os.path.exists(file_path):
            os.remove(file_path)
