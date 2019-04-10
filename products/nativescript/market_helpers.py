import json
import os
import urllib

from core.settings import Settings


class Market(object):

    @staticmethod
    def get_data():
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
                if url:
                    sample_url = flavors[key]
                    record.append(sample_name)
                    record.append(sample_url)
                    record.append(control_string)
                    record.append(key)
                    testing_data.append(record)

        return testing_data

    @staticmethod
    def preserve_data(record):
        # from string to dict - some = ast.literal_eval(test1)
        file_path = os.path.join(Settings.TEST_OUT_HOME, 'results.txt')
        with open(file_path, "a") as myfile:
            myfile.write(str(record)+"\n")
        print "++++============DATA==============++++"
        print record["name"]
        print "Android Pass: " + record["android"]
        print "iOS Pass: " + record["ios"]
        print "++++============END==============++++"

    @staticmethod
    def remove_results_file():
        file_path = os.path.join(Settings.TEST_OUT_HOME, 'results.txt')
        if os.path.exists(file_path):
            os.remove(file_path)
