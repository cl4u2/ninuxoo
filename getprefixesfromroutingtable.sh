#!/bin/bash

ip route sh table 222 | cut -d "/" -f 1 | cut -d "." -f "1-3" | sort | uniq | sed "s/$/./"

