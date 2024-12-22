import yaml
from biot_python_sdk.BioT_API_URLS import * 
from biot_python_sdk.biot import *
def filter_non_versioned_keys(entity_dict):
    nonrelevant_keys=('_creationTime','__reportId','__reportTimestamp','__reportName','_id','_lastModifiedTime','full_patch_json','_referencers','_caption')
    filtered_dict = {k: v for k, v in entity_dict.items() if k not in nonrelevant_keys}
    return filtered_dict

def set_inner_builtin_to_names_only(entity_dict):
    
    for key in entity_dict.keys():
        if type(entity_dict[key])==dict:
            entity_dict[key] = {'name' : entity_dict[key]['name']}
    return entity_dict

def clean_entity_dict_for_repo_json(entity):
    entity = filter_non_versioned_keys(entity)
    entity = set_inner_builtin_to_names_only(entity)
    return entity


def compare_dicts(dict1,dict2,dict1_name,dict2_name,skip_lists=True):
    diff = {}

    # Keys in dict1 but not in dict2
    for key in dict1:
        if skip_lists:
            if type(dict1[key])==list:
                continue
        if key not in dict2:
            diff[key] = {dict1_name: dict1[key], dict2_name: None}
        elif dict1[key] != dict2[key]:
            diff[key] = {dict1_name: dict1[key], dict2_name: dict2[key]}

    # Keys in dict2 but not in dict1
    for key in dict2:
        if key not in dict1:
            diff[key] = {dict1_name: None, dict2_name: dict2[key]}
    if diff!={}:
        return diff
    else:
        return None
    
def compare_lists_of_dicts(list1,list2,list1_name,list2_name):
    diff_dict={}
    for d1 in list1:
        for d2 in list2:
            if d1["_name"]==d2["_name"]:
                diff = compare_dicts(d1,d2,list1_name,list2_name,skip_lists=True)
                if diff:
                    diff_dict[d1["_name"]] = diff
    if diff_dict!=[]:
        return diff_dict
    else:
        return None
    
def compare_if_name_key_in_one_list_only(list_a, list_b,list_a_name,list_b_name):
    names_a = [d['_name'] for d in list_a]
    names_b = [d['_name'] for d in list_b]

    only_in_a = [name for name in names_a if name not in names_b]
    only_in_b = [name for name in names_b if name not in names_a]
    lists_diff = {}
    if only_in_a!=[]:
        lists_diff[f'only_in_{list_a_name}']=only_in_a 
    if only_in_b!=[]:
        lists_diff[f'only_in_{list_b_name}']=only_in_b
    if lists_diff!={}:
        return lists_diff
    else:
        return None


def replace_ref_names_with_ref_id(data_mgr,entity,template_name,org_id):
    if "_ownerOrganization" in entity.keys():
        entity["_ownerOrganization"]["id"] = org_id
        del entity["_ownerOrganization"]["name"]

    with open('ref_mapping.yaml', 'r') as file:
            ref_config = yaml.safe_load(file)

    for key in entity.keys():
        if template_name in ref_config.keys():
            if key in ref_config[template_name]["ref_field"]:
                idx = ref_config[template_name]["ref_field"].index(key)
                ref_template=ref_config[template_name]["ref_template"][idx]
                filter = {"_templateName":{"eq": ref_template},"_name":{"eq":entity[key]["name"]},"_ownerOrganization.id":{"eq":org_id}}
                response = data_mgr.get_ge_by_filter(filter)

                entity[key]["id"] = response["data"][0]["_id"]
                del entity[key]["name"]
    return entity


def remove_internal_dict_to_patch_diffs(entity_diff_dict,keep_ver = 'repo'):
    keys_to_del = []
    fixed_dict = entity_diff_dict.copy()
    if 'channel' in fixed_dict.keys():
        del fixed_dict['channel']
    if 'calibration_step' in fixed_dict.keys():
        del fixed_dict['calibration_step']
    for key in fixed_dict.keys():
        if fixed_dict[key][keep_ver]!= None:
            fixed_dict[key] = fixed_dict[key][keep_ver]
        else:
            keys_to_del.append(key)
    for key in keys_to_del:
        del fixed_dict[key]
    return fixed_dict



def concat_diff_dicts_from_parent_template(state_diff_dict,parent_template,sub_template):

    
    concatenated_diff_dict = {'diffs' : {} ,'only_in_repo' : [],'only_in_biot' : []} 
    if "diffs" in state_diff_dict[parent_template].keys():
        for entity_name in state_diff_dict[parent_template]['diffs'].keys():
            template_diff_dict = state_diff_dict[parent_template]['diffs'][entity_name]
            if sub_template in template_diff_dict.keys():
                if 'only_in_repo' in template_diff_dict[sub_template].keys():
                    concatenated_diff_dict['only_in_repo'].extend(template_diff_dict[sub_template]['only_in_repo'])
                if 'only_in_biot' in template_diff_dict[sub_template].keys():
                    concatenated_diff_dict['only_in_biot'].extend(template_diff_dict[sub_template]['only_in_biot'])
                for key in template_diff_dict[sub_template]['diffs'].keys():
                        concatenated_diff_dict['diffs'][key] =  template_diff_dict[sub_template]['diffs'][key]

    return concatenated_diff_dict


def concat_state_dicts_from_parent_template(state_dict,parent_template,sub_template):


    template_lst = []
    for parent_entity in state_dict[parent_template]:
        if sub_template in parent_entity.keys():
            if sub_template in parent_entity.keys():
                template_lst.extend(parent_entity[sub_template])
    return template_lst
