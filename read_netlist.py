"""
Read netlist file
Performed on 2022 May 05
Daedalus_Digital_Board_050522.qcv
Daedalus_Digital_Board.txt
"""

import time
import math
import os
import string
import csv
from datetime import datetime

def txt_components_on_multiconn_nets(bom_items, multiconn_nets):
    txt_lines = list()
    max_len_part_num_in_bom = 0
    for bom_item in bom_items:
        if len(bom_item['Part Number']) > max_len_part_num_in_bom:
            max_len_part_num_in_bom = len(bom_item['Part Number'])
    str_format = '{:<8}{:<' + str(max_len_part_num_in_bom + 4) + '}{:<8}'
    for multiconn_net in multiconn_nets:
        txt_lines.append('')
        txt_lines.append('-------------------------')
        txt_lines.append('Net Name: {}'.format(multiconn_net['Net Name']))
        txt_lines.append(str_format.format('Amount','Part Number','Value'))
        for bom_item_num in multiconn_net['BOM Item'].keys():
            for bom_item in bom_items:
                if bom_item['#'] == bom_item_num:
                    txt_lines.append(str_format.format(multiconn_net['BOM Item'][bom_item_num],
                                                             bom_item['Part Number'],
                                                             bom_item['Value']))
    for txt_line in txt_lines:
        print(txt_line)
    file_txt_lines = list()
    for txt_line in txt_lines:
        file_txt_lines.append(txt_line + '\n')
    curDT = datetime.now()
    f = open('check_result_{}.txt'.format(curDT.strftime("%m_%d_%Y_%H_%M_%S")), 'w')
    f.writelines(file_txt_lines)
    f.close()


def find_components_on_nets(nets, bom_items, n_conns):
    netname_list = nets.keys()
    multi_conn_net_list = list()
    for netname in netname_list:
        if(len(nets[netname].keys()) > n_conns):
            multi_conn_net_list.append({'Net Name' : netname})
    component_list = nets[netname].keys()
    for component in component_list:
        if(len(nets[netname][component]) > n_conns):
            multi_conn_net_list.append({'Net Name' : netname})
    for multi_conn_net in multi_conn_net_list:
        multi_conn_component_list = nets[multi_conn_net['Net Name']].keys()
        for multi_conn_component in multi_conn_component_list:
            for bom_item in bom_items:
                for bom_component in bom_item['Ref Designator']:
                    if(bom_component == multi_conn_component):
                        if('BOM Item' in multi_conn_net):
                            if bom_item['#'] in  multi_conn_net['BOM Item'].keys():
                                multi_conn_net['BOM Item'][bom_item['#']] += 1
                            else:
                                multi_conn_net['BOM Item'][bom_item['#']] = 1
                        else:
                            multi_conn_net['BOM Item'] = {bom_item['#']:1}
    print(multi_conn_net_list)
    return multi_conn_net_list

def read_bom():
    while True:
        print('Enter BOM (*.txt) file name and path:')
        res = input()
        try:
            f = open(res, "r")
            break
        except (FileNotFoundError, OSError):
            print("File not found.")
    table_keys_line_idx = 0
    # Find the first line of the table
    while True:
        res = f.readline()
        if res.find('#') == -1:
            table_keys_line_idx = table_keys_line_idx + 1
            continue
        else:
            break
    f.seek(0)
    # Read from the first line of the table
    for idx in range(table_keys_line_idx):
        res = f.readline()
        print(res)
    reader = csv.DictReader(f, delimiter='\t', skipinitialspace = True)
    # Move the DictReader to list
    bom_item_list = list()
    for row in reader:
        # Remove space in column name
        for key_name in list(row):
            row[key_name.strip()] = row.pop(key_name)
        # Remove space in column items
        for key_name in list(row):
            if type(row[key_name]) is str:
                row[key_name] = row[key_name].strip()
        bom_item_list.append(row)
    # Combine multi-line components to one line
    for idx_csv_dict in range(len(bom_item_list)):
        if(type(bom_item_list[idx_csv_dict]['#']) is str):
            if(bom_item_list[idx_csv_dict]['#'] == ''):
                for idx_reverse in range(idx_csv_dict):
                    if(bom_item_list[idx_csv_dict - idx_reverse - 1]['#'] == ''):
                        continue
                    else:
                        for key in bom_item_list[idx_csv_dict]:
                            bom_item_list[idx_csv_dict - idx_reverse - 1][key] += bom_item_list[idx_csv_dict][key]
                        break
    # Remove multi-line components
    for csv_dict in list(bom_item_list):
        if(type(csv_dict['#']) is str):
            if(csv_dict['#'] == ''):
                bom_item_list.remove(csv_dict)
        else:
            bom_item_list.remove(csv_dict)
    # Expand '-' in RefDes
    for csv_dict in bom_item_list:
        while(csv_dict['Ref Designator'].find('-') != -1):
            idx_hyphen = csv_dict['Ref Designator'].find('-')
            idx_hyphen_begin = csv_dict['Ref Designator'].rfind(',', 0, idx_hyphen)
            if(idx_hyphen_begin == -1):
                idx_hyphen_begin = 0
            else:
                idx_hyphen_begin += 1
            idx_hyphen_end = csv_dict['Ref Designator'].find(',', idx_hyphen)
            if(idx_hyphen_end == -1):
                idx_hyphen_end = len(csv_dict['Ref Designator'])
            str_num_hyphen_front = ''
            str_num_hyphen_rear = ''
            str_component_ref = ''
            for z in csv_dict['Ref Designator'][idx_hyphen_begin:idx_hyphen]:
                if z.isdigit():
                    str_num_hyphen_front += z
                else:
                    str_component_ref += z
            num_hyphen_front = int(str_num_hyphen_front)
            for z in csv_dict['Ref Designator'][idx_hyphen:idx_hyphen_end]:
                if z.isdigit():
                    str_num_hyphen_rear += z
            num_hyphen_rear = int(str_num_hyphen_rear)
            str_replacing = ','
            for idx_num_components in range(num_hyphen_front + 1, num_hyphen_rear):
                str_replacing += str_component_ref
                str_replacing += str(idx_num_components)
                str_replacing += ','
            csv_dict['Ref Designator'] = csv_dict['Ref Designator'].replace('-',str_replacing,1)
    # Replace RefDes String with list
    for csv_dict in bom_item_list:
        csv_dict['Ref Designator'] = csv_dict['Ref Designator'].split(',')
        print(csv_dict)
    return bom_item_list

def read_netlist():
    while True:
        print('Enter Netlist (*.qcv) file name and path:')
        res = input()
        try:
            f = open(res, "r")
            break
        except (FileNotFoundError, OSError):
            print("File not found.")

    line_list = f.readlines()
    nets = dict()
    for res in line_list:
        if res.find('NET : ') == -1 :
            continue
        net_name_start = res.find('\'')
        net_name_end = res.find('\'', net_name_start + 1)
        netname = res[net_name_start + 1 : net_name_end]
        print(netname)
        component_name_start = net_name_end
        component_pin_dict = dict()
        while True:
            pin_list = list()
            component_name_start = res.find(' ', component_name_start + 1)
            pin_name_end = res.find(' ', component_name_start + 1)
            if pin_name_end == -1 :
                pin_name_start = res.find('-', component_name_start + 1, len(res) - 1)
                if res[component_name_start + 1 : pin_name_start] in component_pin_dict:
                    component_pin_dict[res[component_name_start + 1 : pin_name_start]].append(res[pin_name_start + 1 :  len(res) - 1])
                else:
                    pin_list.append(res[pin_name_start + 1 :  len(res) - 1])
                    component_pin_dict[res[component_name_start + 1 : pin_name_start]] = pin_list
                break
            else :
                pin_name_start = res.find('-', component_name_start + 1, len(res) - 1)
                if res[component_name_start + 1 : pin_name_start] in component_pin_dict:
                    component_pin_dict[res[component_name_start + 1 : pin_name_start]].append(res[pin_name_start + 1 :  pin_name_end])
                else:
                    pin_list.append(res[pin_name_start + 1 :  pin_name_end])
                    component_pin_dict[res[component_name_start + 1 : pin_name_start]] = pin_list
                component_name_start = pin_name_end - 1
        print(component_pin_dict)
        nets[netname] = component_pin_dict
    return nets


def main():
    nets = read_netlist()
    bom_items = read_bom()
    multiconn_nets = find_components_on_nets(nets, bom_items, 5)
    txt_components_on_multiconn_nets(bom_items, multiconn_nets)

if __name__ == '__main__':
    main()