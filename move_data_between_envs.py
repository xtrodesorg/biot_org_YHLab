import requests
#from biot_python_sdk.biot import *
from biot_python_sdk_local.biot import *
from State import StateDiff,OrgState
from login import get_access_token
from constants import *


if __name__=='__main__':
    usernames = ['amiel.w@xtrodes.com','amiel.w@xtrodes.com']
    passwords = ['Xtr@56130','Xtr@56130!!']
    user_agent='Mozilla/5.0 (X11; Linux x86_64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

    manufacturer_id = '00000000-0000-0000-0000-000000000000'
    src_org_id = manufacturer_id  # in dev env
    dest_org_id = '93e3b0ac-03ab-464d-8792-d27867893bd2' # in prod env
    
    montages_names=['Test 1.5 8Ch EMG']
    sensor_names = []
    patch_names=[] #['EMG-8ch']
    assests_to_assign_dict={'montage_configuration': montages_names,'sensor':sensor_names,'patch':patch_names}
    
    envs = ('development','production')
    report_names = ['yael_dev','yael_copy_from_dev']

    tokens = ['','']
    api_clients = [None,None]
    biot_clients = [None,None]
    data_mgrs = [None,None]
    report_mgrs = [None,None]
    base_urls = [DEV_BASE_URL,PROD_BASE_URL]


    for i,env in enumerate(envs):    

        tokens[i] = get_access_token(usernames[i],passwords[i],env)
        api_clients[i] = APIClient(base_url=base_urls[i])
        biot_clients[i] = BiotClient(api_clients[i], token=tokens[i])
        data_mgrs[i] = DataManager(biot_clients[i],allow_delete=True)
        report_mgrs[i] = ReportManager(data_mgrs[i])
        #response = report_mgrs[i].export_full_configuration_snapshot(report_names[i])
        #print(response)

    #input('Press Enter Once Reports Created')

    report_data_dict = report_mgrs[0].get_report_file_by_name(report_names[0])
    report_data_dict = report_mgrs[1].config_report_to_different_org(src_org_id, dest_org_id, report_data_dict)
    report_data_dict = report_mgrs[1].filter_report_for_copy(report_data_dict, assests_to_assign_dict)
    report_mgrs[1].post_full_configuration_report(report_data_dict)

    
    report_mgrs[i].export_full_configuration_snapshot(report_names[i]+'_post')
    save_state = input('Save state in github? [y/n]:')
    if save_state.lower()=='y':
        response = report_mgrs[i].export_full_configuration_snapshot(report_names[i])
        report_name = f'dest_org_{dest_org_id}'
        input('Press Enter Once Report Created')
        test_org_state=OrgState(dest_org_id,report_name,'production',usernames[1],passwords[1])
        test_org_state.push_state_to_github()
        test_org_diff_state = StateDiff(test_org_state)
    pass