#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Release 0.0.5 of Oct 26, 2016

# for access to MySQL DB need install pymysql module. For it need execute the next:
# set https_proxy=username:pass@proxysg01 :8080
# set http_proxy=username:pass@proxysg01 :8080
# easy_install pymysql


import os
import pymysql
import datetime
import data_struct
import logger


def eis_selection(eis_list, host, user, passwd):
  '''Method for extracting different'''

  connection = pymysql.connect(host, user, passwd, db='REPORTS', charset='utf8')
  connection.use_unicode =  True
  try:
    with connection.cursor() as cursor:

      closed_tickets, resolved_tickets, postponed_tickets, active_standby_tickets, departure_tickets, departure_as_stage_tickets \
      = [], [], [], [], [], []

      # Read and selection of closed EIs
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=9"
      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          closed_tickets.append(i)
      print('Closed EIs ({0}):\n {1}'.format(len(closed_tickets), closed_tickets))

      # Read and selection of resolved EIs
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=5"
      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          resolved_tickets.append(i)
      print('Resolved EIs ({0}):\n {1}'.format(len(resolved_tickets), resolved_tickets))
      
      # Read and selection of postponed EIs
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=12"
      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          postponed_tickets.append(i)
      print('Postponed EIs ({0}):\n {1}'.format(len(postponed_tickets), postponed_tickets))
      
      # Read and selection of active standby EIs
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=4"
      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          active_standby_tickets.append(i)
      print('Active standby EIs ({0}):\n {1}'.format(len(active_standby_tickets), active_standby_tickets))      


      
      # search the value for departure_group_id in db
      sql = "SELECT remedy_group_id, group_name FROM LEGEND_group_list"
      cursor.execute(sql)
      remedy_group_id_and_group_name = cursor.fetchall()
      for i in remedy_group_id_and_group_name:
        if  i[-1].encode('utf-8') == b'\xd0\x92\xd1\x8b\xd0\xb5\xd0\xb7\xd0\xb4': # this byte's string means 'Выезд'
          departure_group_id = i[0]

      # Read and selection: status - active standby EIs AND WHERE remedy_group_id='MSK000000000076' (departure)
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=4 AND remedy_group_id='" + departure_group_id + "'"

      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          departure_tickets.append(i)
      
      print('Departure EIs ({0}):\n {1}'.format(len(departure_tickets), departure_tickets))

      # Read and selection: status - assigned EIs AND WHERE remedy_group_id='MSK000000000076' (departure)
      sql = "SELECT remedy_id FROM tt_list WHERE remedy_id=%s AND status=2 AND remedy_group_id='" + departure_group_id + "'"

      for i in eis_list:
        cursor.execute(sql, i)
        selection = cursor.fetchall()
        if selection != ():
          departure_as_stage_tickets.append(i)
      
      print('Departure AS STAGE EIs ({0}):\n {1}'.format(len(departure_as_stage_tickets), departure_as_stage_tickets))
      
      # Writing to file
      tofile = open('tickets.txt', 'w')
      
      tofile.write('Closed IEs ({0}):\n'.format(len(closed_tickets)))
      for i in closed_tickets:
        tofile.write(str(i)+'\n')
      
      tofile.write('\nResolved IEs ({0}):\n'.format(len(resolved_tickets)))
      for i in resolved_tickets:
        tofile.write(str(i)+'\n')
      
      tofile.write('\nPostponed IEs ({0}):\n'.format(len(postponed_tickets)))
      for i in postponed_tickets:
        tofile.write(str(i)+'\n')
        
      tofile.write('\nActive standby IEs ({0}):\n'.format(len(active_standby_tickets)))
      for i in active_standby_tickets:
        tofile.write(str(i)+'\n')
        
      tofile.write('\nDeparture IEs ({0}):\n'.format(len(departure_tickets)))
      for i in departure_tickets:
        tofile.write(str(i)+'\n')
        
      tofile.write('\nDeparture AS STAGE IEs ({0}):\n'.format(len(departure_as_stage_tickets)))
      for i in departure_as_stage_tickets:
        tofile.write(str(i)+'\n')

  finally:
    connection.close()
    return [closed_tickets, resolved_tickets, postponed_tickets, active_standby_tickets, departure_tickets,            departure_as_stage_tickets]

def actual_eis_selection(host, user, passwd):
  '''Method for extracting actual eis'''
    
  connection = pymysql.connect(host, user, passwd, db='REPORTS', charset='utf8')
  connection.use_unicode =  True
  try:
    with connection.cursor() as cursor:
      
      technologies = ['PON', 'ADSL', 'АТШ']

      for technology in technologies:
      # Reading and selecting tickets by technology
        sql = '''SELECT si.remedy_id, gr.group_name, si.create_date FROM tt_list si
        LEFT JOIN LEGEND_all_menus me ON si.ChannelType = me.id AND me.menuname = "ChannelType"
        LEFT JOIN LEGEND_group_list gr ON si.remedy_group_id = gr.remedy_group_id
        WHERE si.status <> 5 AND si.status <> 9
        AND si.SEGMENT = "МР"
        AND (si.MI_ID is NULL OR si.MI_ID = 0)
        AND si.SOURCE =  2000000908750 #АСРЗ
        AND me.value LIKE "%{0}%"
        '''.format(technology)
        cursor.execute(sql)
        selection = cursor.fetchall()
        for i in selection:
          if selection != ():
            data_struct.Ticket(*i, technology=technology)
      
      # Counting actual tickets_by_technology
      numbers_of_tickets_by_technology = {'PON': 0, 'ADSL': 0, 'АТШ': 0}
      for technology in numbers_of_tickets_by_technology:
        for ticket in data_struct.Ticket.tickets:
          if ticket.technology == technology:
            numbers_of_tickets_by_technology[technology]+=1
      print('Numbers of actual tickets sorted by technology:', [[key, numbers_of_tickets_by_technology[key]] for key in sorted(numbers_of_tickets_by_technology)])
  
  finally:
    connection.close()
    return data_struct.Ticket.tickets


def date2unix(data):
  '''Transform date and time to unix time.'''
  return int(datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').timestamp())

def record_updater_in_db(host, user, passwd, records):
  '''Method for updating record in db (will update: rec_group, comment, update_time), or create record if one doesn't exist in db.'''

  #NEED WRITE check for case if current day is now equal record date, then update record group!
  # NNED WRITE checker for inserted and updated strings!!!

  recs = []
  for rec in records:
    recs.append(rec.ticket.remedy_id)
  recs = tuple(recs)

  remedy_id_list, rec_group_list, comment_list, update_time_list = [], [], [], []
  for rec in records:
    remedy_id_list.append(str(rec.ticket.remedy_id))
    rec_group_list.append(str(rec.ticket.ticket_group))
    comment_list.append(str(rec.comment))
    update_time_list.append(str(date2unix(rec.rec_upd_time)))

  remedy_id_list = tuple(remedy_id_list)
  rec_group_list = tuple(rec_group_list)
  comment_list = tuple(comment_list)
  update_time_list = tuple(update_time_list)

  rec_s_without_remedy_id = str(tuple(zip(rec_group_list, comment_list, update_time_list)))[1:-1]
  rec_s = str(tuple(zip(remedy_id_list, rec_group_list, comment_list, update_time_list)))[1:-1]

  print(recs)
  connection = pymysql.connect(host, user, passwd, db='coordination', charset='utf8')
  connection.use_unicode =  True
  try:
    with connection.cursor() as cursor:
      # Comparing list of input records vs records in db and finding general records
      sql = '''SELECT rl.remedy_id, rl.rec_group, rl.comment, rl.update_time from records_list rl
      WHERE rl.remedy_id IN {0}
      '''.format(recs)
      cursor.execute(sql)
      selection = cursor.fetchall()
      print('selection:', selection)
      if selection:
        # update the record
        # sql = '''UPDATE records_list 
        #SET rec_group = '{rec_group}', comment = '{comment}', update_time = {update_time}
        #'''.format(rec_group = record.ticket.ticket_group, comment = record.comment, update_time = date2unix(record.rec_upd_time))
        
        sql='''INSERT INTO records_list (remedy_id, rec_group, comment, update_time) VALUES {rec_s} 
        ON DUPLICATE KEY UPDATE remedy_id=VALUES(remedy_id),rec_group=VALUES(rec_group),comment=VALUES(comment), update_time=VALUES(update_time)
        '''.format(rec_s = rec_s)
        cursor.execute(sql)


      else:
        # INSERT the RECORD to db, if record doesn't exist
        remedy_id_list, rec_group_list, comment_list, update_time_list = [], [], [], []
        for rec in records:
          remedy_id_list.append(str(rec.ticket.remedy_id))
          rec_group_list.append(str(rec.ticket.ticket_group))
          comment_list.append(str(rec.comment))
          update_time_list.append(str(date2unix(rec.rec_upd_time)))

        remedy_id_list = tuple(remedy_id_list)
        rec_group_list = tuple(rec_group_list)
        comment_list = tuple(comment_list)
        update_time_list = tuple(update_time_list)

        rec_s = str(tuple(zip(remedy_id_list, rec_group_list, comment_list, update_time_list)))[1:-1]

        sql = '''INSERT INTO records_list (remedy_id, rec_group, comment, update_time) 
        VALUES {rec_s}
        '''.format(rec_s = rec_s)
        cursor.execute(sql)
        connection.commit()
        # need raise the exception ??
        error = "{date_time} In DB doesn't exist record with remedy_id: {remedy_id}".format(date_time = str(datetime.datetime.now()), remedy_id = record.ticket.remedy_id)
        logger.insert_error(error)

  finally:
    connection.close()



def reading_settings():
  '''Reading settings (host, user & passwd fro reading & for writing) from .ini file.'''
  settings_file_name = 'settings.ini'
  options = []
  host, user, passwd = '', '', ''
  if not os.access(settings_file_name, os.F_OK):
    print("We wait a file: {0}".format(current_file_name[1:]))
    print("Copy this file to root app folder and restart this app again!")
  else:
    with open(settings_file_name, 'r') as settings_file:
      settings = settings_file.readlines()
  
  for line in settings:
    string = line.strip().split()
    if len(string) >= 2:
      options.append(string[1])
    elif len(string) == 1:
      options.append('')
  
  for_reading, for_writing = [], []
  if len(options) == 3:
    for_reading = for_writing = options
  else:
    for_reading, for_writing = options[:3], options[3:]
  
  # data format in for_reading and in for_writing is next: host, user, passwd

  return [[for_reading[0], for_reading[1], for_reading[2]], [for_writing[0], for_writing[1], for_writing[2]]]

if __name__ == '__main__':
  eis_list = ['E01811977', 'E01812707', 'E01813703', 'E01817779', 'E01818531', 'E01818803', 'E01818876',
  'E01820336', 'E01820733', 'E01821330', 'E01821611', 'E01821781', 'E01822127', 'E01822756', 'E01822903',
  'E01847357', 'E01847331', 'E01847527', 'E01847904', 'E01848027', 'E01848504', 'E01848930', 'E01849376',
  'E01849580', 'E01849587', 'E01849698', 'E01849657', 'E01849754', 'E01850128', 'E01850628', 'E01850677',
  'E01851877', 'E01852676', 'E01852802', 'E01853119', 'E01853436', 'E01853597', 'E01854632', 'E01854752',
  'E01855026', 'E01855027', 'E01855337', 'E01855429', 'E01856026', 'E01856904', 'E01857427', 'E01857531',
  'E01857791', 'E01858030', 'E01858379', 'E01858729', 'E01859078', 'E01860002', 'E01860301', 'E01861051',
  'E01863753', 'E01863929', 'E01863954', 'E01822928'
  ]

  auth_data_for_reading, auth_data_for_writing = reading_settings()
  
  closed_tickets, resolved_tickets, postponed_tickets, active_standby_tickets, departure_tickets, departure_as_stage_tickets = eis_selection(eis_list, *auth_data_for_reading)
  actual_eis = actual_eis_selection(*auth_data_for_reading)
  
  for ei in actual_eis:
    record = data_struct.Record(ei)
    print(record)
    print(ei)
      
  

  # for rec in record.records:
  record_updater_in_db(*auth_data_for_writing, records=record.records)
  
