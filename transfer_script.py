import requests
from biot_python_sdk.biot import *
from State import StateDiff,OrgState
from login import get_access_token
from constants import *


if __name__=='__main__':
    username = 'amiel.w@xtrodes.com'
    password = 'Xtr@56130'
    user_agent='Mozilla/5.0 (X11; Linux x86_64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

    manufacturer_id = '00000000-0000-0000-0000-000000000000'
    test_org_id = 'c130d275-901b-4ca9-bc54-c064bf09e599'
    
    env= 'development'

    token = get_access_token(username,password,env)
    api_client = APIClient(base_url=DEV_BASE_URL)
    biot_client = BiotClient(api_client, token=token)
    data_mgr = DataManager(biot_client,allow_delete=True)
    report_mgr = ReportManager(data_mgr)


    #report_name ='xtrodes&test_org_3'
    report_name = 'xtrodes&test_org_4'
    #response = report_mgr.export_full_configuration_snapshot(report_name)
    print('Press Enter When report Created')
    #input()

    env='development'
    test_org_state=OrgState(test_org_id,report_name,env,username,password)
    #test_org_state.push_state_to_github()
    test_org_diff_state = StateDiff(test_org_state)
    test_org_diff_state.revert_to_repo_state()