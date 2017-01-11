#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime

class Ticket:
  '''A ticket class'''

  tickets = []
  def __init__(self, remedy_id=None, ticket_group=None, ticket_time=None, technology=None):
    
    self.remedy_id = remedy_id
    self.ticket_group = ticket_group
    self.ticket_time = ticket_time
    self.technology = technology
    self.tickets.append(self)
  
  def __str__(self):
    return 'Ticket: {0}, {1}, {2}, {3}'.format(self.remedy_id, self.ticket_group, self.ticket_time, self.technology)

class Record(Ticket):
  '''A record class'''
  
  records = []
  def __init__(self, ticket=None, rec_group=None, comment=None, rec_upd_time=None):
    self.ticket = ticket
    if rec_group == None:
      self.rec_group = ticket.ticket_group
    else:
      self.rec_group = rec_group
    self.comment = comment
    if rec_upd_time != None:
      self.rec_upd_time = rec_upd_time
    else:
      self.rec_upd_time = str(datetime.now())[:-7] 
    self.records.append(self)

  def __str__(self):
    if self.ticket != None:
      return 'Record: ' +  '{0}, {1}, {2}, {3}, {4}, {5}'.format(self.ticket.remedy_id, self.rec_group, self.ticket.ticket_time, self.ticket.technology, self.comment, self.rec_upd_time)

class Report:
  '''A report class'''
  
  def __init__(self, *args):
    self.records = list(args)

  def show_all(self):
    for record in self.records:
      print(record)
 

if __name__ == '__main__':
  t1 = Ticket('E001', 'IPTV and telematics')
  t2 = Ticket('E002', 'DPI')
  t3 = Ticket({'remedy_id': 'E003', 'ticket_group': 'MIKS', 'ticket_time': '2016-11-21 13:53:29'})
  t4 = Ticket('E002', 'DPI')
  rec1 = Record(Ticket())
  rec2 = Record(t1, 'at Nov 20: everything is sad')
  rec3 = Record(t2)
  rec4 = Record(t3)
  rec5= Record(t4)
  print(t1)
  report = Report(*rec1.records)
  report.show_all()

