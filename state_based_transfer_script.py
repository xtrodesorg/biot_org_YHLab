from constants import *
from biot_python_sdk.biot import *
from State import OrgState
from login import get_access_token
from constants import *
#from revert_to_release import revert_to_release



if __name__=='__main__':
    
    #call function 
    yael_lab_name = 'YHLab'
    xtrodes_org_name = 'xtrodes1'
    env='production'
    yael_lab_state_prod=OrgState(yael_lab_name,env,PROD_USERNAME,PROD_PASSWORD)
    #env='development'
    #xtrodes_state_dev=OrgState(xtrodes_org_name,env,DEV_USERNAME,DEV_PASSWORD)
    #xtrodes_state_dev.push_state_to_repo_with_release()
    '''
    emg_g_montage = xtrodes_state_dev.biot_state_dict["montage_configuration"][29]
    emg_g_montage['_ownerOrganization']['name'] = yael_lab_name
    for template in ('channel','calibration_step'):
        for i in range(len(emg_g_montage[template])):
            emg_g_montage[template][i]['_ownerOrganization']['name'] = yael_lab_name
    '''
    #yael_lab_state_prod.biot_state_dict["montage_configuration"].append(emg_g_montage)
    yael_lab_state_prod.push_state_to_repo_with_release()
    #yael_lab_state_prod.push_state_to_repo_with_release()
