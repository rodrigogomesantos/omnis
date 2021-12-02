_format = "%m/%d/%Y, %H:%M:%S"
# pylint: disable=no-member

import json as js
import os
from pathlib import Path
from datetime import datetime, timedelta
from cv2 import add
from numpy import average, around, save
from os.path import exists as file_exists
from os import makedirs
import re

class json(object):
    def __init__(self, path, name, script_dir, **args):
        self.name = name+".json"
        self.dir = os.path.join(script_dir, path)
        self.data = args.get("data")
        self.value = self.open(self.dir) if not self.data else self.data

    def self(self):
        return self.value

    def add(self, key, value):
        self.value[key] = value

    def pop(self, key):
        self.value.pop(key, None)
        
    # Abre e lê um json no caminho solicitado.
    def open(self, path):
        if isinstance(path, str):
            with open(f"{path}", 'r', encoding='utf8') as json_file:
                return js.load(json_file)
        elif isinstance(path, dict):
            return path


    # Abre e grava um json no caminho solicitado.
    def save(self, **args):
        json_data = args.get("data")
        if json_data:
            self.value  = json_data
        with open(f"{self.dir}", "w", encoding='utf8') as jsonFile:
            js.dump(self.value, jsonFile, indent=4, ensure_ascii=False)

class production(object):
    def __init__(self, data_dir, modelo, template, script_dir, **kwargs):
        
        self.data_path = data_dir
        self.model = modelo
        self.template = template
        self.autoSave = kwargs.get("autoSave")
        self.control_objects = {}
        path = f"{data_dir}/{self.model['name']}/"
        if not os.path.exists(script_dir+path):
            makedirs(script_dir+path)
        for key, value in self.template.items():
            if not file_exists(script_dir+path+f"{key}.json"):
                if key == "info":
                    value["date"] = (datetime.now()).strftime(_format)
                    for k,v in self.model.items():
                        print(k,v)
                        value[k] = v
                _file = json(path+f"{key}.json", key, script_dir, data=value)
                _file.save()
            else:
                _file = json(path+f"{key}.json", key, script_dir)
            setattr(self,key, _file)
            self.control_objects[key] = getattr(self, key)

        self.kwargs = kwargs
    def is_another_day(self):
        return ((datetime.strptime(self.info.value["date"], _format).day - datetime.now().day) != 0)

    def add(self, where, what, amount):
        getattr(self, where).value[what] += amount
        self.get_total(where)

    def remove(self, where, what, amount):
        getattr(self, where).value[what] -= amount
        self.get_total(where)

    def define(self, where, what, amount):
        getattr(self, where).value[what] = amount
        self.get_total(where)

    def get_total(self, where) -> int:
        atribute = getattr(self, where)
        value = atribute.value["rigth"]+atribute.value["wrong"]
        atribute.value["total"] = value
        if self.autoSave: self.save()
        return value
        

    def add2day(self, what, amount):
        if self.is_another_day():
            self.update_avarage()
            self.reset_day()
        self.add("today", what, amount)
        self.add("total", what, amount)

    def remove2day(self, what, amount, *args):
        print(what,amount,*args)
        if self.is_another_day():
            self.update_avarage()
            self.reset_day()
        else:
            self.remove("today", what, amount)
            self.remove("total", what, amount)

    def reset_day(self):
        self.info.value["date"] = (datetime.now()).strftime(_format)
        self.today.value = self.template["today"]

    def update_avarage(self):
        for key in self.avarage.value.keys():
            self.avarage.value[key].append({(datetime.strptime(self.info.value["date"], _format)).timestamp():self.today.value[re.search("\_(.*)", key).group()[1:]]})
            if len(self.avarage.value[key]) > self.info.value["avarage_size"]:
                self.avarage.value[key] = self.avarage.value[key][-self.info.value["avarage_size"]:]

    def save(self):
        for obj in self.control_objects.values():
            obj.save()