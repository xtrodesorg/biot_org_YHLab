from State import OrgState
from constants import *


def revert_to_release(org_name,release_tag,env):
    
    if env == 'development':
        USERNAME = DEV_USERNAME
        PASSWORD = DEV_PASSWORD
    elif env =='production':
        USERNAME = PROD_USERNAME
        PASSWORD = PROD_PASSWORD
        
    org_state=OrgState(org_name,env,USERNAME,PASSWORD,release_tag)
    org_state.revert_to_repo_state()

if __name__=='__main__':
    
    revert_to_release(ORG_NAME,RELEASE_TAG,ENV)





