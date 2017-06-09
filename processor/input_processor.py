#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, date
import parsedatetime as pdt
import time
import json
import re


def process_input(slots):
   

    a = {}
    for index,slot in enumerate(slots):
        if slot == '':
            continue
        slot = slot.split('\t')

      #  print slot[0], '\t', slot[1], '\t', slot[2]
        a[index] = {"value":slot[0],"intent":slot[2]}
    return a



			