#!/bin/bash

#Run script for the server distributed as a part of 
#Assignment 1
#Computer Networks (CS 456 / CS 656)
#
#Number of parameters: 2
#Parameter:
#    $1: <req_code>
#    $2: <req_lim>

#Uncomment exactly one of the following commands depending on implementation

#For C/C++ implementation
#./server $1 $2

#For Java implementation
#java server $1 $2

#For Python implementation
python server.py $1 $2

#For Ruby implementation
#ruby server.rb $1 $2
