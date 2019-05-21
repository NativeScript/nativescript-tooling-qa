import json
import os
import urllib

from datetime import date
from core.log.log import Log
from core.settings import Settings

class FlavorStatus(object):
    def setAndroid(self, value):
        self.android = value
    def getAndroid(self):
        return self.android

    def setIOS(self, value):
        self.ios = value
    def getIOS(self):
        return self.ios
        
    def setSlow(self, value):
        self.slow = value
    def getSlow(self):
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

        return testing_data


    def get_preserved_data():
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.json')
        data = None
        if os.path.isfile(file_path):
            with open(file_path, "r") as jsonFile:
                data = json.load(jsonFile)
        else:
            with open(file_path, "w") as newFile:
                Log.info("Results.json file created")

        return data

    def serialize(obj):
        if isinstance(obj, date):
            serial = obj.isoformat()
            return serial

        return obj.__dict__

    @staticmethod
    def preserve_data(record):
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.json')
        preserved_data = Market.get_preserved_data()
        tempSampleStatus = None
        recordName = record["name"]
        originalIndex = None

        if preserved_data:
            tempSampleStatus = next((x for x in preserved_data if x["name"] == recordName), None)
            if tempSampleStatus != None:
                originalIndex = preserved_data.index(tempSampleStatus)
        else:
            preserved_data = []
        
        if tempSampleStatus == None:
            tempSampleStatus = {
                "name": recordName,
                "core": None,
                "angular": None,
                "vue": None
            }
        
        if record["flavor"] == "core":
            tempSampleStatus["core"] = Market.serialize(Market.get_flavor_status(record))

        if record["flavor"] == "angular":
            tempSampleStatus["angular"] = Market.serialize(Market.get_flavor_status(record))

        if record["flavor"] == "vue":
            tempSampleStatus["vue"] = Market.serialize(Market.get_flavor_status(record))

        if originalIndex == None:
            preserved_data.append(tempSampleStatus)
        else:
            preserved_data[originalIndex] = tempSampleStatus

        with open(file_path, "w") as jsonFile:
            json.dump(preserved_data, jsonFile, indent=4)

        Log.info("++++============DATA==============++++")
        Log.info(record["name"])
        Log.info("Android Pass: " + record["android"])
        Log.info("iOS Pass: " + record["ios"])
        Log.info("++++============END==============++++")

    def get_flavor_status(record):
        tempFlavorStatus = FlavorStatus()
        tempFlavorStatus.setAndroid(Market.convert_to_bool(record["android"]))
        tempFlavorStatus.setIOS(Market.convert_to_bool(record["ios"]))
        tempFlavorStatus.setSlow(Market.convert_to_bool(record["slow"]))

        return tempFlavorStatus

    def convert_to_bool(value):
        return value.lower() in ("yes", "true", "t", "1")

    @staticmethod
    def remove_results_file():
        file_path = os.path.join(Settings.TEST_RUN_HOME, 'results.txt')
        if os.path.exists(file_path):
            os.remove(file_path)
