from biot_python_sdk.biot import *
from biot_python_sdk.BioT_API_URLS import *

from utils.json_processing import *
def get_ge_name_from_id(ge_id,data_mgr):
   response = data_mgr._make_authenticated_request(f'{GENERIC_ENTITES_URL}/{ge_id}')

   return response['data'][0]['_name']


def get_clean_ge_by_template_org(data_mgr,org_id,template_name,montage_field_filt = None , montage_id_filt = None):
   
   
   filter = {"_templateName":{"eq": template_name },"_ownerOrganization.id":{"eq":org_id}}
   if montage_id_filt and montage_field_filt:
      filter[f"{montage_field_filt}.id"] = {"eq":montage_id_filt}
   response = data_mgr.get_ge_by_filter(filter)
   e_lst = []
   for e in response['data']:
      e_lst.append(clean_entity_dict_for_repo_json(e))
   return e_lst


def post_entity_from_repo_by_template(template_diff_dict,template_repo_lst,template,org_id,data_mgr):
   #add post
   for e_name in template_diff_dict["only_in_repo"]:
      for e_repo in template_repo_lst:
         if e_repo["_name"]==e_name:
            e_repo = replace_ref_names_with_ref_id(data_mgr,e_repo,template,org_id)
            del e_repo["_template"] 
            post_dict = e_repo.copy()
            if template=="montage_configuration":
               del post_dict["calibration_step"]
               del post_dict["channel"]
            response = data_mgr._make_authenticated_request(GENERIC_ENTITES_URL+f'/templates/{template}','POST',post_dict)
            print(response)
            print(response.content)
            if template=="montage_configuration":
               for sub_template in ("channel","calibration_step"):
                     for sub_e_repo in e_repo[sub_template]:
                        sub_e_repo = replace_ref_names_with_ref_id(data_mgr,sub_e_repo,sub_template,org_id)
                        del sub_e_repo["_template"]
                        response = data_mgr._make_authenticated_request(GENERIC_ENTITES_URL+f'/templates/{sub_template}','POST',sub_e_repo)
                        print(f'Entity {e_name} of template {template} Posted, {response} \n')
            break



def revert_template_to_repo(org_state,template):
   
      nested_templates = {"calibration_step":"montage_configuration","channel":"montage_configuration"}
      if template in nested_templates.keys():

         template_diff_dict = concat_diff_dicts_from_parent_template(org_state.state_diff_dict,nested_templates[template],template)
         template_repo_lst = concat_state_dicts_from_parent_template(org_state.repo_state_dict,nested_templates[template],template)
      else:
         if template in  org_state.state_diff_dict.keys():
            template_diff_dict = org_state.state_diff_dict[template]
            template_repo_lst = org_state.repo_state_dict[template]
         else:
            template_diff_dict={}
      for change_type in template_diff_dict.keys():

         match change_type:
            case "diffs":
               template_diffs_dict = template_diff_dict[change_type]
               for e_name in template_diffs_dict.keys():
                  
                  entity_patch_dict = remove_internal_dict_to_patch_diffs(template_diffs_dict[e_name])
                  entity_patch_dict["_name"] = e_name
                  entity_patch_dict = replace_ref_names_with_ref_id(org_state.data_mgr,entity_patch_dict,template,org_state.org_id)

                  filter = {"_templateName":{"eq": template},"_name":{"eq":e_name},"_ownerOrganization.id":{"eq":org_state.org_id}}
                  response = org_state.data_mgr.get_ge_by_filter(filter)
                  e_id = response["data"][0]["_id"]
                  response = org_state.data_mgr._make_authenticated_request(GENERIC_ENTITES_URL+f'/{e_id}','PATCH',entity_patch_dict)
                  print(f'Entity {e_name} of template {template} Patched, {response} \n')
                  print('Fields Updated: ',entity_patch_dict)

            case "only_in_repo":
               #add post
               post_entity_from_repo_by_template(template_diff_dict,template_repo_lst,template,org_state.org_id,org_state.data_mgr)
            case "only_in_biot":
               for e_name in template_diff_dict[change_type]:
                  to_del=input(f'Entity to Delete: {e_name} of template {template} \n Confirm Delete [Y/N]: \n')
                  if to_del.lower()=='y':
                     filter = {"_templateName":{"eq": template},"_name":{"eq":e_name},"_ownerOrganization.id":{"eq":org_state.org_id}}
                     response = org_state.data_mgr.get_ge_by_filter(filter)
                     e_id = response["data"][0]["_id"]
                     response = org_state.data_mgr._make_authenticated_request(GENERIC_ENTITES_URL+f'/{e_id}','DELETE')
                     print(f'Entity {e_name} of template {template} Deleted' ,response)
                  else:
                     print('Skipping Delete')
                  #add delete
            case _:
               pass
   