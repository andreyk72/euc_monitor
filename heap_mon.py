#!/usr/bin/env python3

from esp32 import idf_heap_info, HEAP_DATA

def heap_info(label):
    res = idf_heap_info(HEAP_DATA)
    print(label, 'free:', [r[1] for r in res])
