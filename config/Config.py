from pprint import pprint

import yaml


class Config:
    config = {}

    def load():
        with open("config.yaml") as stream:
            try:
                Config.config = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)

        print("Loaded Config")
        pprint(Config.config)
