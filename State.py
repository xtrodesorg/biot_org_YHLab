import os
from biot_python_sdk.biot import *
from biot_python_sdk import BioT_API_URLS
from login import get_access_token
from utils.git import * 
from utils.json_processing import *
from utils.biot_helpers import *
from constants import *
from datetime import datetime

DEV_BASE_URL = 'https://api.dev.xtrodes1.biot-med.com'
PROD_BASE_URL = 'https://api.xtrodes.biot-med.com'

class OrgState:
    def __init__(self,org_name,env,username,password,release_tag= None):
        
        self.env = env
        if env == 'production':
            BASE_URL = PROD_BASE_URL
        elif env == 'development':
            BASE_URL = DEV_BASE_URL
        token = get_access_token(username,password,env)
        api_client = APIClient(base_url=BASE_URL)
        biot_client = BiotClient(api_client, token=token)
        self.data_mgr = DataManager(biot_client,allow_delete=True)
        self.report_mgr = ReportManager(self.data_mgr)
    
        self.org_id = self.data_mgr._get_org_id_from_name(org_name)
        self.org_name = org_name
        

        self.biot_state_time_stamp = None
        self.load_state_from_biot()
        if not release_tag:
            self.load_current_repo_state()
            self.repo_state_release_tag= None
        else:
            self.load_release_repo_state(release_tag)
            self.repo_state_release_tag= release_tag
        self.check_repo_and_biot_diffs()


    def push_state_to_repo_with_release(self): #decide repo name format
        file_name = self._format_file_state_name()

        with open(file_name, 'w') as f:
            json.dump(self.biot_state_dict, f)
        branch_name = self.env
        repo_name = f'biot_org_{self.org_name}'
        commit_file(repo_name, branch_name,GITHB_TOKEN,file_name)
        #add relase
        #create_realese()

    def load_current_repo_state(self):
        repo_name = f'biot_org_{self.org_name}'
        file_name = self._format_file_state_name()
        branch_name = self.env
        clone_git_repo(repo_name,GITHB_TOKEN)
        os.chdir(repo_name)
        subprocess.call(["git" ,"checkout", f"{branch_name}"])
        try:
            with open(file_name,'r') as f:
                state_json_str=f.read()
                self.repo_state_dict = json.loads(state_json_str)
        except:
            print("No configuration file in repo")
            self.repo_state_dict = {"montage_configuration": [] ,"sensor":[] ,"patch":[] }
        os.chdir('..')

    def load_release_repo_state(self,release_tag):
        
        release_files = get_release_files(self.org_name, release_tag)
        self.repo_state_dict  = json.loads(release_files[f'biot_org_{self.org_name}_state.json'])
        pass

    def load_state_from_biot(self):
        self.biot_state_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filter = {"_templateName":{"eq":"montage_configuration"},"_ownerOrganization.id":{"eq":self.org_id}}
        m_response = self.data_mgr.get_ge_by_filter(filter)
        montages_lst = list()
        
        for m in m_response["data"]:
            m_dict = clean_entity_dict_for_repo_json(m)
            


            clb_steps_lst = get_clean_ge_by_template_org(self.data_mgr,self.org_id,"calibration_step","montage_calibraterd" , m["_id"])
            channel_lst = get_clean_ge_by_template_org(self.data_mgr,self.org_id,"channel","montage_configuration" , m["_id"])
            m_dict['calibration_step'] = clb_steps_lst
            m_dict['channel'] = channel_lst

            montages_lst.append(m_dict)

        sensor_lst = get_clean_ge_by_template_org(self.data_mgr,self.org_id,"sensor")
        patch_lst = get_clean_ge_by_template_org(self.data_mgr,self.org_id,"patch")


        biot_state_dict = {"montage_configuration":montages_lst,"sensor":sensor_lst,"patch":patch_lst}
        self.biot_state_dict =biot_state_dict


    def load_repo_state_From_release(self):
        pass
    def check_repo_and_biot_diffs(self):
        
        state_diff_dict = {}
        
        for template in ('montage_configuration','patch','sensor'):
            
            miss_add_diff_dict = compare_if_name_key_in_one_list_only(self.biot_state_dict[template], self.repo_state_dict[template],'biot','repo')
            existing_with_diff_dict = compare_lists_of_dicts(self.biot_state_dict[template], self.repo_state_dict[template],'biot','repo')
            if miss_add_diff_dict:
                state_diff_dict[template] = miss_add_diff_dict
            if existing_with_diff_dict:
                if template not in state_diff_dict.keys():
                    state_diff_dict[template]={}
                state_diff_dict[template]['diffs'] = existing_with_diff_dict
        
        for montage_biot in self.biot_state_dict["montage_configuration"]:
            for montage_repo in self.repo_state_dict["montage_configuration"]:
                if montage_repo["_name"]==montage_biot["_name"]:
                    for template in ('channel','calibration_step'): 
                        miss_add_diff_dict = compare_if_name_key_in_one_list_only(montage_biot[template], montage_repo[template],'biot','repo')
                        existing_with_diff_dict = compare_lists_of_dicts(montage_biot[template], montage_repo[template],'biot','repo')
                        if miss_add_diff_dict:
                            if "montage_configuration" not in state_diff_dict.keys():
                                state_diff_dict["montage_configuration"] = {"diffs":{montage_biot["_name"] : {}}}
                            if montage_biot["_name"] not in state_diff_dict["montage_configuration"]['diffs'].keys():
                                state_diff_dict["montage_configuration"]['diffs'][montage_biot["_name"]]={}
                            state_diff_dict["montage_configuration"]['diffs'][montage_biot["_name"]][template]= miss_add_diff_dict
                        if existing_with_diff_dict:
                            if "montage_configuration" not in state_diff_dict.keys():
                                state_diff_dict["montage_configuration"] = {"diffs":{montage_biot["_name"] : {}}}
                            if montage_biot["_name"] not in state_diff_dict["montage_configuration"]['diffs'].keys():
                                state_diff_dict["montage_configuration"]['diffs'][template][montage_biot["_name"]]={}
                            if template not in state_diff_dict["montage_configuration"]['diffs'][montage_biot["_name"]].keys():
                                state_diff_dict["montage_configuration"]['diffs'][montage_biot["_name"]][template]={}
                            
                            state_diff_dict["montage_configuration"]['diffs'][montage_biot["_name"]][template]['diffs'] = existing_with_diff_dict
                    break    
        self.state_diff_dict =state_diff_dict
                    

    def revert_to_repo_state(self):
        if self.state_diff_dict!={}:
            templates_order = ("patch", "montage_configuration", "channel","calibration_step","sensor")
            # fields to fic (owner_org, template,refs[]list)
            for template in templates_order:
                revert_template_to_repo(self,template)
        else:
            print("No Reversions Need. States Already Synced")
        
       
    
    def _format_file_state_name(self): 
        return f'biot_org_{self.org_name}_state.json'

    def check_for_floating_ge(self):
        pass

