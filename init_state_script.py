from biot_python_sdk.biot import *
from State import OrgState
from login import get_access_token
from constants import *



PASSWORD = os.environ['PASSWORD']
USERNAME = os.environ['USERNAME']


if __name__=='__main__':
   
    org_name = 'test_org'
    env= 'development'
    
    test_org_state=OrgState(org_name,env,USERNAME,PASSWORD)
    test_org_state.revert_to_repo_state()
    #test_org_state.push_state_to_repo_with_release()
    pass