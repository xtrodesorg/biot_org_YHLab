
def filter_non_versioned_keys(entity_dict):
    nonrelevant_keys=('_creationTime','__reportId','__reportTimestamp','__reportName','_id','_lastModifiedTime','full_patch_json','_referencers')
    filtered_dict = {k: v for k, v in entity_dict.items() if k not in nonrelevant_keys}
    return filtered_dict

def compare_dict_lists(list_a, list_b,list_a_name,list_b_name):
    names_a = [d['_name'] for d in list_a]
    names_b = [d['_name'] for d in list_b]

    only_in_a = [d for d in list_a if d['_name'] not in names_b]
    only_in_b = [d for d in list_b if d['_name'] not in names_a]

    in_both_with_diff_list_a_version = []
    in_both_with_diff_list_b_version = []
    for d_a in list_a:
        f_d_a = filter_non_versioned_keys(d_a)
        for d_b in list_b:
            f_d_b = filter_non_versioned_keys(d_b)
            if d_a['_name'] == d_b['_name']:
                if f_d_a != f_d_b:
                    in_both_with_diff_list_a_version.append(d_a)
                    in_both_with_diff_list_b_version.append(d_b)
                    break
    lists_diff= {f'only_in_{list_a_name}':only_in_a, 
                 f'only_in_{list_b_name}':only_in_b,
                'in_both_diff_values':{list_a_name:in_both_with_diff_list_a_version,
                                       list_b_name:in_both_with_diff_list_b_version}} 
    return lists_diff

def format_report_line_api(entity):
    post_json=dict()
    keys_to_del = ('full_patch_json','montage_image','_templateId')  # work around for get montages plugin.
    if entity['_template']['name']=='montage_configuration':
        if 'full_patch_json' in entity.keys():
            del entity['full_patch_json']
        if 'montage_image' in entity.keys():
            del entity['montage_image']
    if entity['_template']['name']=='sensor':
        if 'device' in entity.keys():
            del entity['device']
    
    for key in entity.keys():
        post_json['_ownerOrganization'] = {'id':entity['_ownerOrganization']['id']}
        post_json['_name'] = entity['_name']
        if key[0]!='_': # not built in attribute
            if type(entity[key])==dict:
                post_json[key] = {'id':entity[key]['id']}
            elif key not in keys_to_del:
                post_json[key] = entity[key]
    return post_json