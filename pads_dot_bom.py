"""
Read netlist file
Performed on 2023 Feb 03
daedalus_digital_board_14-09-22.bom
"""

import time
import os
import string
import tabulate
from datetime import datetime

def print_dict_in_table(dict_to_print):
        header = dict_to_print[0].keys()
        rows =  [x.values() for x in dict_to_print]
        print(tabulate.tabulate(rows, header))

def get_partial_dict(full_dict, key_index):
    if len(full_dict) > max(key_index):
        key_list = list(full_dict.keys())
        value_list = list(full_dict.values())
        partial_keys = list()
        partial_values = list()
        for idx in key_index:
            partial_keys.append(key_list[idx])
            partial_values.append(value_list[idx])
        partial_dict = dict(zip(partial_keys, partial_values))
        return partial_dict
    else:
        return full_dict

def check_bom_item_number(bom_dict_list, item_number):
    for bom_dict in bom_dict_list:
        if bom_dict['ITEM_NUMBER'] == str(item_number):
            table_bom_dict_list = list()
            table_bom_dict_list.append(get_partial_dict(bom_dict, [0,1,2,3,4,5,6]))
            print_dict_in_table(table_bom_dict_list)

def check_refdes(bom_dict_list, ref_des):
    for bom_dict in bom_dict_list:
        if bom_dict['REFERENCE NAME'].count(ref_des):
            found_ref_des_from_dict = bom_dict
    if found_ref_des_from_dict != '':
        table_bom_dict_list = list()
        table_bom_dict_list.append(get_partial_dict(found_ref_des_from_dict, [0,1,2,3,4,5,6]))
        print_dict_in_table(table_bom_dict_list)

def remove_refdes_from_bom_dict_list(bom_dict_list, dict_idx_to_remove, ref_des, confirm_idx_to_join):
    bom_dict_list[dict_idx_to_remove]['REFERENCE NAME'].remove(ref_des)
    bom_dict_list[dict_idx_to_remove]['COUNT'] = str(int(bom_dict_list[dict_idx_to_remove]['COUNT']) - 1)
    if bom_dict_list[dict_idx_to_remove]['COMMENT'] == '---':
        bom_dict_list[dict_idx_to_remove]['COMMENT'] = ''.join((ref_des, ' replaced to ITEM_NUMBER ', str(confirm_idx_to_join + 1)))
    else:
        bom_dict_list[dict_idx_to_remove]['COMMENT'] += (''.join(('; ', ref_des, ' replaced to ITEM_NUMBER ', str(confirm_idx_to_join + 1))))

def add_refdes_to_bom_dict_list(bom_dict_list, confirm_idx_to_join, ref_des, dict_idx_to_remove):
    bom_dict_list[confirm_idx_to_join]['REFERENCE NAME'].append(ref_des)
    bom_dict_list[confirm_idx_to_join]['REFERENCE NAME'].sort()
    bom_dict_list[confirm_idx_to_join]['COUNT'] = str(int(bom_dict_list[confirm_idx_to_join]['COUNT']) + 1)
    if bom_dict_list[confirm_idx_to_join]['COMMENT'] == '---':
        bom_dict_list[confirm_idx_to_join]['COMMENT'] = ''.join((ref_des, ' added from ITEM_NUMBER ', str(dict_idx_to_remove + 1)))
    else:
        bom_dict_list[confirm_idx_to_join]['COMMENT'] += (''.join(('; ', ref_des, ' added from ITEM_NUMBER ', str(dict_idx_to_remove + 1))))

def read_bom():
    while True:
        print('Enter BOM (*.bom) file name and path:')
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
        if res.find('#') != -1:
            table_keys_line_idx = table_keys_line_idx + 1
            continue
        elif res.replace(' ', '') == '\n':
            table_keys_line_idx = table_keys_line_idx + 1
            continue
        else:
            break
    f.seek(0)
    # Read from the first line of the table
    for idx in range(table_keys_line_idx):
        res = f.readline()
        print(res)

    res = f.readline()
    headers = res.split('  ')
    for idx, header in enumerate(headers):
        headers[idx] = header.strip()
    while headers.count('') != 0:
        headers.remove('')

    header_index_list = list()
    for header in headers:
        header_index_list.append(res.find(header))

    bom_dict_list = list()
    dict_item_list = list()
    while True:
        res = f.readline()
        if res == '':
            break
        elif res.strip() == '':
            continue
        elif res[header_index_list[0]:header_index_list[1]].strip() == headers[0]:
            break

        if res[header_index_list[0]:header_index_list[1]].strip() == '':
            ref_des = res[header_index_list[4]:header_index_list[5]].strip()
            comment = res[header_index_list[5]:header_index_list[6]].strip()
            if ref_des != '':
                bom_dict_list[-1][headers[4]].extend(ref_des.split(' '))
            if comment != '':
                bom_dict_list[-1][headers[5]] += (' ' + comment)
        else:
            if dict_item_list:
                dict_item_list.clear()
                
            dict_item_list.append(res[header_index_list[0]:header_index_list[1]].strip())
            dict_item_list.append(res[header_index_list[1]:header_index_list[2]].strip())
            dict_item_list.append(res[header_index_list[2]:header_index_list[3]].strip())
            dict_item_list.append(res[header_index_list[3]:header_index_list[4]].strip())
            ref_des = res[header_index_list[4]:header_index_list[5]].strip()
            if ref_des != '':
                dict_item_list.append(ref_des.split(' '))
            else:
                dict_item_list.append(list())
            dict_item_list.append(res[header_index_list[5]:header_index_list[6]].strip())
            dict_item_list.append(res[header_index_list[6]:-1].strip())
            bom_dict_list.append(dict(zip(headers, dict_item_list)))
    return bom_dict_list, header_index_list, os.path.basename(f.name)

def check_bom(bom_dict_list):
    empty_item_list = list()
    ref_des_list = list()
    for bom_dict in bom_dict_list:
        if int(bom_dict['COUNT']) != len(bom_dict['REFERENCE NAME']):
            print('ITEM_NUMBER: ', bom_dict['ITEM_NUMBER'], ' --- UNCHECK')
        else:
            print('ITEM_NUMBER: ', bom_dict['ITEM_NUMBER'], ' --- CHECKED')
            
        if int(bom_dict['COUNT']) == 0:
            empty_item_list.append(bom_dict_list.index(bom_dict) + 1)

        ref_des_list.extend(bom_dict['REFERENCE NAME'])

    ref_des_list.sort()
    print('Total ref-des Count: ', len(ref_des_list), ':', ref_des_list)
    ref_des_set = set(ref_des_list)
    if len(ref_des_list) == len(ref_des_set):
        print('No duplicate RefDes found.')
    else:
        print('ERROR: Duplicate RefDes found.')

def modify_bom(bom_dict_list):
    # Input RefDes to be changed
    remove_ref_des_from_dict = ''
    while True:
        ref_des = input('\nRefDes to be changed:')
        for bom_dict in bom_dict_list:
            if bom_dict['REFERENCE NAME'].count(ref_des):
                remove_ref_des_from_dict = bom_dict
        if remove_ref_des_from_dict != '':
            break
    temp_list = list()
    temp_list.append(get_partial_dict(remove_ref_des_from_dict, [0,1,2,3,5,6]))
    print_dict_in_table(temp_list)

    # Confirm Remove RefDes from BOM ITEM
    while True:
        y_or_n = input(''.join(('\nConfirm Remove ', ref_des, ' from ITEM_NUMBER ', remove_ref_des_from_dict['ITEM_NUMBER'], '?'))).lower()
        if y_or_n.startswith('n'):
            return
        elif y_or_n.startswith('y'):
            break
    dict_idx_to_remove = bom_dict_list.index(remove_ref_des_from_dict)

    # Search for BOM ITEM modification Keyword
    bom_dict_selec_list = list()
    keywords = input('\nTry to Add to Another BOM Item by Entering KeyWord of Description or COMPANY PART NO:')
    for bom_dict in bom_dict_list:
        if bom_dict == bom_dict_list[dict_idx_to_remove]:
            continue
        elif keywords == '':
            if bom_dict['DESCRIPTION'] == '':
                bom_dict_selec_list.append(bom_dict_list.index(bom_dict))
        elif bom_dict['DESCRIPTION'].lower().find(keywords.lower()) != -1:
            bom_dict_selec_list.append(bom_dict_list.index(bom_dict))
        elif bom_dict['COMPANY PART NO'].lower().find(keywords.lower()) != -1:
            bom_dict_selec_list.append(bom_dict_list.index(bom_dict))

    # Keyword found in Existing BOM ITEM
    if len(bom_dict_selec_list) > 0:
        table_bom_dict_selec = list()
        for bom_dict_selec in bom_dict_selec_list:
            table_bom_dict_selec.append(get_partial_dict(bom_dict_list[bom_dict_selec], [0,1,2,3,5,6]))
        print_dict_in_table(table_bom_dict_selec)

        # Join Removed BOM ITEM to Existing ITEM
        while True:
            j_or_c = input(''.join(('\n [J]oin ', ref_des, ' to one of the above BOM ITEMS or [C]reate a new BOM ITEM for ', ref_des, ', J or C?'))).lower()
            if j_or_c == 'j':
                while True:
                    idx_to_join = input('Enter ITEM_NUMBER Listed above:')
                    if idx_to_join.isdigit():
                        confirm_idx_to_join = ''
                        for bom_dict_selec in bom_dict_selec_list:
                            if bom_dict_list[bom_dict_selec]['ITEM_NUMBER'] == idx_to_join:
                                confirm_idx_to_join = bom_dict_selec
                        if confirm_idx_to_join != '':
                            break
                table_bom_dict_list = list()
                table_bom_dict_list.append(get_partial_dict(remove_ref_des_from_dict, [0,1,2,3,5,6]))
                table_bom_dict_list.append(get_partial_dict(bom_dict_list[confirm_idx_to_join], [0,1,2,3,5,6]))
                print('\n\nRemove RefDes ', ref_des, ' from the 1st following BOM ITEM to the 2nd:')
                print_dict_in_table(table_bom_dict_list)
                y_or_n = input(''.join(('\nConfirm Above Operation?'))).lower()
                if y_or_n.startswith('y'):
                    # Removing RefDes
                    remove_refdes_from_bom_dict_list(bom_dict_list, dict_idx_to_remove, ref_des, confirm_idx_to_join)

                    # Adding RefDes
                    add_refdes_to_bom_dict_list(bom_dict_list, confirm_idx_to_join, ref_des, dict_idx_to_remove)
                    table_bom_dict_list = list()
                    table_bom_dict_list.append(get_partial_dict(bom_dict_list[dict_idx_to_remove], [0,1,2,3,5,6]))
                    table_bom_dict_list.append(get_partial_dict(bom_dict_list[confirm_idx_to_join], [0,1,2,3,5,6]))
                    print_dict_in_table(table_bom_dict_list)
                    print('Done')
                break
            elif j_or_c == 'c':
                break
    else:
        print('\nKeyword not found in Existing BOM ITEMS! New BOM ITEM will be Created.')
        # Prepare for keyword not found
        j_or_c = 'c'
        
    # Create New BOM Item
    if j_or_c == 'c':
        dict_template = bom_dict_list[dict_idx_to_remove].copy()
        dict_key_list = dict_template.keys()
        for dict_key in dict_key_list:
            if dict_key == 'ITEM_NUMBER':
                dict_template[dict_key] = str(int(bom_dict_list[-1]['ITEM_NUMBER']) + 1)
            elif dict_key == 'REFERENCE NAME':
                dict_template[dict_key] = list()
                dict_template[dict_key].append(ref_des)
            elif dict_key == 'COUNT':
                dict_template[dict_key] = '1'
            elif dict_key == 'COMMENT':
                dict_template[dict_key] = ''.join(('Added ', ref_des, ' from ITEM_NUMBER ', str(dict_idx_to_remove + 1)))
            else:
                print(dict_key, ': ', dict_template[dict_key])
                while True:
                    y_or_n = input(''.join(('Enter yes to change ', dict_key, ', y or n?'))).lower()
                    if y_or_n.startswith('n'):
                        break
                    elif y_or_n.startswith('y'):
                        bom_text_revision = input('Enter BOM Content Revision Text:')
                        dict_template[dict_key] = bom_text_revision
                        break

        temp_list = list()
        similar_bom_item_list = list()
        for bom_dict in bom_dict_list:
            if bom_dict == bom_dict_list[dict_idx_to_remove]:
                continue
            elif bom_dict['COMPANY PART NO'].lower() == dict_template['COMPANY PART NO'].lower():
                temp_list.append(get_partial_dict(bom_dict, [0,1,2,3,5,6]))
                similar_bom_item_list.append(bom_dict_list.index(bom_dict))
            elif bom_dict['DESCRIPTION'].lower() == dict_template['DESCRIPTION'].lower():
                temp_list.append(get_partial_dict(bom_dict, [0,1,2,3,5,6]))
                similar_bom_item_list.append(bom_dict_list.index(bom_dict))
        if len(similar_bom_item_list) > 0:
            print('\nFound Similar BOM ITEMs:')
            print_dict_in_table(temp_list)
            print('\nOr Add New BOM ITEM:')
        else:
            print('\nAdd New BOM ITEM:')
        temp_list = list()
        temp_list.append(get_partial_dict(dict_template, [0,1,2,3,5,6]))
        print_dict_in_table(temp_list)

        table_bom_dict_list = list()
        table_bom_dict_list.append(get_partial_dict(remove_ref_des_from_dict, [0,1,2,3,5,6]))
        confirm_idx_to_join = ''
        confirm_to_add = False
        while True:
            print('\nEnter Yes to Add New Created BOM ITEM;')
            if len(similar_bom_item_list) > 0:
                print('Enter ITEM_NUMBER in above table for Joining Existing BOM ITEM;')
                j_or_y_or_n = input(''.join(('Enter No to Discard Change, y or n or number?'))).lower()
            else: 
                j_or_y_or_n = input(''.join(('Enter No to Discard Change, y or n?'))).lower()
            if j_or_y_or_n.isdigit() and len(similar_bom_item_list) > 0:
                if similar_bom_item_list.count(int(j_or_y_or_n) - 1) > 0:
                    confirm_idx_to_join = int(j_or_y_or_n) - 1
                    table_bom_dict_list.append(get_partial_dict(bom_dict_list[confirm_idx_to_join], [0,1,2,3,5,6]))
                    break
            elif j_or_y_or_n.startswith('y'):
                confirm_to_add = True
                table_bom_dict_list.append(get_partial_dict(dict_template, [0,1,2,3,5,6]))
                break
            elif j_or_y_or_n.startswith('n'):
                return
        print('\n\nRemove RefDes ', ref_des, ' from the 1st following BOM ITEM to the 2nd:')
        print_dict_in_table(table_bom_dict_list)

        y_or_n = input(''.join(('\nConfirm Above Operation?'))).lower()
        if y_or_n.startswith('y'):
            if confirm_to_add:
                bom_dict_list.append(dict_template)
                confirm_idx_added = bom_dict_list.index(dict_template)
            elif confirm_idx_to_join != '':
                add_refdes_to_bom_dict_list(bom_dict_list, confirm_idx_to_join, ref_des, dict_idx_to_remove)
                confirm_idx_added = confirm_idx_to_join

            remove_refdes_from_bom_dict_list(bom_dict_list, dict_idx_to_remove, ref_des, confirm_idx_added)
            table_bom_dict_list = list()
            table_bom_dict_list.append(get_partial_dict(bom_dict_list[dict_idx_to_remove], [0,1,2,3,5,6]))
            table_bom_dict_list.append(get_partial_dict(bom_dict_list[confirm_idx_added], [0,1,2,3,5,6]))
            print_dict_in_table(table_bom_dict_list)
            print('Done')

def print_bom(bom_dict_list, header_index_list, filename):
    header_index_list[6] = 131
    while True:
        print('Enter New BOM (*.bom) file name and path:')
        print('Modified from ', filename)
        res = input()
        try:
            f = open(res, "w")
            break
        except (FileNotFoundError, OSError):
            print("File exist.")

    header_lines = list()
    header_lines.append(''.join(('# Bill of Materials - Modified from ', filename, '\n')))
    header_lines.append('# date: ' + str(datetime.now()) + '\n')
    header_lines.append('\n')
    header_lines.append('\n')
    header_lines.append('\n')
    f.writelines(header_lines)

    bom_dict_key_list = bom_dict_list[0].keys()
    
    bom_key_string = ''
    for idx, bom_dict_key in enumerate(bom_dict_key_list):
        while len(bom_key_string) < header_index_list[idx]:
            bom_key_string += ' '
        bom_key_string += bom_dict_key
    bom_key_string += '\n'
    bom_key_list = list()
    bom_key_list.append(bom_key_string)
    bom_key_list.append('\n')
    f.writelines(bom_key_list)

    bom_item_list = list()
    for bom_dict in bom_dict_list:
        bom_item_string = ''
        refdes_remain_list = list()
        comment_str_remain_list = list()
        for idx, bom_dict_key in enumerate(bom_dict_key_list):
            while len(bom_item_string) < header_index_list[idx]:
                bom_item_string += ' '
            if idx != 4 and idx != 5:
                bom_item_string += bom_dict[bom_dict_key]
            elif idx == 4:
                refdes_list = bom_dict[bom_dict_key].copy()
                while len(' '.join(refdes_list)) > (header_index_list[5] - header_index_list[4] - 4):
                    refdes_remain_list.append(refdes_list.pop())
                bom_item_string += ' '.join(refdes_list)
                refdes_remain_list.reverse()
            elif idx == 5:
                comment_str_list = bom_dict[bom_dict_key].split()
                while len(' '.join(comment_str_list)) > (header_index_list[6] - header_index_list[5] - 4):
                    comment_str_remain_list.append(comment_str_list.pop())
                bom_item_string += ' '.join(comment_str_list)
                comment_str_remain_list.reverse()
                
        bom_item_string += '\n'
        bom_item_list.append(bom_item_string)
        while len(refdes_remain_list) > 0 or len(comment_str_remain_list) > 0:
            bom_item_string = ''
            if len(refdes_remain_list) > 0:
                bom_item_string += ' ' * header_index_list[4]
                refdes_list = refdes_remain_list.copy()
                refdes_remain_list.clear()
                while len(' '.join(refdes_list)) > (header_index_list[5] - header_index_list[4] - 4):
                    refdes_remain_list.append(refdes_list.pop())
                bom_item_string += ' '.join(refdes_list)
                refdes_remain_list.reverse()
            if len(comment_str_remain_list) > 0:
                bom_item_string += ' ' * (header_index_list[5] - len(bom_item_string))
                comment_str_list = comment_str_remain_list.copy()
                comment_str_remain_list.clear()
                while len(' '.join(comment_str_list)) > (header_index_list[6] - header_index_list[5] - 4):
                    comment_str_remain_list.append(comment_str_list.pop())
                bom_item_string += ' '.join(comment_str_list)
                comment_str_remain_list.reverse()
            bom_item_string += '\n'
            bom_item_list.append(bom_item_string)
    f.writelines(bom_item_list)

def print_bom_csv(bom_dict_list, filename):
    while True:
        print('Enter New BOM (*.csv) file name and path:')
        print('Modified from ', filename)
        res = input()
        try:
            f = open(res, "w")
            break
        except (FileNotFoundError, OSError):
            print("File exist.")

    bom_dict_key_list = bom_dict_list[0].keys()
    column_count = len(bom_dict_key_list)
    bom_dict_key_str_list = list()
    for bom_dict_key in bom_dict_key_list:
        bom_dict_key_str_list.append(str(bom_dict_key))
    bom_dict_order = [0, 1, 2, 3, 4, 6, 5]
    bom_dict_key_order_list = [bom_dict_key_str_list[idx] for idx in bom_dict_order]

    header_lines = list()
    header_lines.append(''.join(('# Bill of Materials - Modified from ', filename, ',' * (column_count - 1), '\n')))
    header_lines.append('# date: ' + str(datetime.now()) + ',' * (column_count - 1) + '\n')
    header_lines.append(',' * (column_count - 1) + '\n')
    header_lines.append(',' * (column_count - 1) + '\n')
    header_lines.append(',' * (column_count - 1) + '\n')
    f.writelines(header_lines)

    bom_item_list = list()
    bom_item_list.append(','.join(bom_dict_key_order_list) + '\n')
    for bom_dict in bom_dict_list:
        bom_dict_value_str_list = list()
        bom_dict_value_list = bom_dict.values()
        for bom_dict_value in bom_dict_value_list:
            if isinstance(bom_dict_value, str):
                bom_dict_value_str_list.append(bom_dict_value)
            elif isinstance(bom_dict_value, list):
                bom_dict_value_str_list.append(' '.join(bom_dict_value))
        bom_dict_value_str_order_list = [bom_dict_value_str_list[idx] for idx in bom_dict_order]
        bom_item_list.append(','.join(bom_dict_value_str_order_list) + '\n')
    f.writelines(bom_item_list)

def main():
    bom_items, header_index_list, filename = read_bom()
    check_bom(bom_items)
    print(header_index_list)
    while True:
        print('\nMenu:')
        print('Check BOM ITEM_NUMBER  : CHECK BOM [idx]')
        print('Check RefDes           : CHECK REFDES [idx]')
        print('Modify BOM             : MODIFY BOM')
        print('Print BOM as .bom      : PRINT BOM')
        print('Print BOM as .csv      : PRINT CSV')
        selec_menu = input('\nSelect Operation from Above List:').upper()
        if selec_menu.startswith('CHECK BOM '):
            if selec_menu[10:].isdigit():
                check_bom_item_number(bom_items, int(selec_menu[10:]))
        elif selec_menu.startswith('CHECK REFDES '):
            check_refdes(bom_items, selec_menu[13:])
        elif selec_menu.startswith('MODIFY BOM'):
            modify_bom(bom_items)
            check_bom(bom_items)
        elif selec_menu.startswith('PRINT BOM'):
            print_bom(bom_items, header_index_list, filename)
        elif selec_menu.startswith('PRINT CSV'):
            print_bom_csv(bom_items, filename)


if __name__ == '__main__':
    main()