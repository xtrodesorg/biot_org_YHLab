import os
from biot_python_sdk.biot import *
from biot_python_sdk import BioT_API_URLS
from login import get_access_token
from utils.git import * 
from utils.data_proc import *
from constants import *


class OrgState:
    def __init__(self,org_id,report_name,env,username,password):
        token = get_access_token(username,password,env)
        api_client = APIClient(base_url=BASE_URL)
        biot_client = BiotClient(api_client, token=token)
        self.data_mgr = DataManager(biot_client,allow_delete=True)
        self.report_mgr = ReportManager(self.data_mgr)

        self.org_id=org_id
        self.state_dict={}
        self.based_report_name = report_name
        self.env = env

        response=self.data_mgr._make_authenticated_request( ORGANIZATION_URL+f'/{org_id}', method='GET', json=None)
        org_dict = response.json()
        self.org_name = org_dict['_name']
        self.state_dict=self.format_report_to_state_dict(report_name)

    def push_state_to_github(self): #decide repo name format
        file_name = self._format_file_state_name()
        with open(file_name, 'w') as f:
            json.dump(self.state_dict, f)
        branch_name = self.env
        repo_name = f'biot_org_{self.org_name}'
        commit_file(repo_name, branch_name,GITHUB_TOKEN,file_name)
  
    
    def get_json_from_repo(self):
        repo_name = f'biot_org_{self.org_name}'
        file_name = self._format_file_state_name()
        branch_name = self.env
        clone_git_repo(repo_name,GITHUB_TOKEN)
        os.chdir(repo_name)
        subprocess.call(["git" ,"checkout", f"{branch_name}"])
        with open(file_name,'r') as f:
            state_json_str=f.read()
        current_repo_state= json.loads(state_json_str)

        return current_repo_state

    def format_report_to_state_dict(self,report_name):
        ge_state_dict = {'montage_configuration':[],'channel':[],'calibration_step':[],'patch':[],'sensor':[]}
        report_data=self.report_mgr.get_report_file_by_name(report_name)
        device_state_list =report_data['device']
        ge_report = report_data['generic-entity']
        for ge_dict in ge_report:
            if ge_dict['_ownerOrganization']['id']==self.org_id:
                ge_state_dict[ge_dict['_template']['name']].append(ge_dict)
        return {'generic-entity':ge_state_dict,'device': device_state_list }
    
    def _format_file_state_name(self): 
        return f'biot_org_{self.org_name}_state.json'


    def switch_envs(env,user_agent,username,password):
        pass


class StateDiff:

    def __init__(self,org_state):

        #support devices to.
        self.org_state =org_state
        self.report_mgr =org_state.report_mgr
        self.data_mgr = org_state.report_mgr.data_mgr
        self.diff_ge_state_dict=self.compare_biot_and_repo_states()
        pass

    def compare_biot_and_repo_states(self):
   
        diff_ge_state_dict = {'montage_configuration':[],'channel':[],'calibration_step':[],'patch':[],'sensor':[]}
        state_repo_dict=self.org_state.get_json_from_repo()
        ge_state_repo_dict = state_repo_dict['generic-entity']
        biot_ge_state_dict=self.org_state.state_dict['generic-entity']
        
        for ge_template in biot_ge_state_dict.keys():
            diff_ge_state_dict[ge_template]=compare_dict_lists(biot_ge_state_dict[ge_template], ge_state_repo_dict[ge_template],'biot','repo')
            pass
        return diff_ge_state_dict


    def revert_to_repo_state(self):
        
        ge_to_add_list=[]
        ge_state_dict=self.org_state.state_dict['generic-entity']
        assests_to_assign_dict={'montage_configuration': [],'sensor':[],'patch':[]}
        
        templates_parents_dict = {'calibration_step':'montage_calibraterd','channel':'montage_configuration'}
        #check for entity with missing links->delte.
        for tempalte in templates_parents_dict.keys():
            for e in ge_state_dict[tempalte]:
                missing_reference = False
                if templates_parents_dict[tempalte] in e.keys():
                    if e[templates_parents_dict[tempalte]]=={} or e[templates_parents_dict[tempalte]]==None:
                        missing_reference=True
                    #check if parent in to add. -> if not add to GE to add.
                else:
                    missing_reference=True
                if missing_reference:
                    if tempalte not in ('calibration_step','channel'):
                        assests_to_assign_dict[tempalte].append(e['_name'])
                    #response = self.data_mgr._make_authenticated_request(f'{GENERIC_ENTITES_URL}/{e['_id']}',method='DELETE')
                    #print(e['_name'],'delete attempt reponse:',response)

        #1. delete extra ge
        for template in self.diff_ge_state_dict.keys():
            
            #1. delete extra ge
            for entity in self.diff_ge_state_dict[template]['only_in_biot']:
                response = self.data_mgr._make_authenticated_request(f'{GENERIC_ENTITES_URL}/{entity['_id']}',method='DELETE')
                print(entity['_name'],'delete attempt reponse:',response)
    
            #2.  add new ge
            if template in assests_to_assign_dict.keys():
                for e in self.diff_ge_state_dict[template]['only_in_repo']:
                    assests_to_assign_dict[template].append(e['_name'])
            else:
                for e in self.diff_ge_state_dict[template]['only_in_repo']:
                   for key in e.keys():
                       if 'montage' in key:
                           filter= {"_name":{"eq":e[key]["name"]},"_templateName": {"eq": "montage_configuration"}, "_ownerOrganization.id": {"eq": self.org_state.org_id}}
                           response = self.data_mgr.get_ge_by_filter( filter)
                           if response:
                            if response['data']!=[]:
                                self.report_mgr.post_report_json([e],'generic-entity')

            #3.  update differnce
            if self.diff_ge_state_dict[template]['in_both_diff_values']['repo']!=[]:
                for entity in self.diff_ge_state_dict[template]['in_both_diff_values']['repo']:
                    post_json=format_report_line_api(entity)
                    endpoint=f'{GENERIC_ENTITES_URL}/{entity['_id']}'
                    response = self.data_mgr._make_authenticated_request(endpoint=endpoint, method='PATCH',json=post_json)
                    if response:
                        print(response,':' ,response.content)
                    
        self.org_state.report_mgr.full_org_transfer_wrapper(manufacturer_id,self.org_state.org_id,self.org_state.based_report_name,assests_to_assign_dict)