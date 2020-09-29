#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt
#current_directory =os.path.dirname(sys.argv[0]) 
#dirname = os.path.dirname(os.path.realpath(__file__))
#print(current_directory)
#apro connessione Oracle
#print(os.path.dirname(os.path.realpath('test_parametri.py')))
print('il percorso al file è ', os.getcwd()) 
sys.path.insert(0, r'C:\Users\assis\Documents\GitHub\oracle_sdo_crs')
from .credenziali import *
print(host)