#!/bin/bash
TABLE=main

ip route sh table $TABLE | cut -d "/" -f 1 | cut -d "." -f "1-3" | sort | uniq | sed "s/$/./" | sort -R

