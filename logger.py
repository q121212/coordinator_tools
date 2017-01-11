#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

def insert_error(error):
  print(error)
  if os.path.isfile('errors.log'):
    with open('errors.log', 'a') as f:
      f.write(error + '\n')
  else:
    with open('errors.log', 'w') as f:
      f.write(error + '\n')

if __name__ == '__main__':
  # insert_error('err')
  pass