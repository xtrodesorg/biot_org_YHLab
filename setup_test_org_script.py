import requests
from biot_python_sdk.biot import *
from State import StateDiff,OrgState
from login import get_access_token
from constants import *

from biot_python_sdk.biot import *
from biot_python_sdk.BioT_API_URLS import *

if __name__=='__main__':
    username = 'amiel.w@xtrodes.com'
    password = 'Xtr@56130'

    manufacturer_id = '00000000-0000-0000-0000-000000000000'
    test_org_id = 'cff35ecc-2b18-4878-98b0-191eb328a640'

    env= 'development'
    token = get_access_token(username,password,env)
    api_client = APIClient(base_url=BASE_URL)
    biot_client = BiotClient(api_client, token=token)
    data_mgr = DataManager(biot_client,allow_delete=False)
    report_mgr = ReportManager(data_mgr)


    #montages_names= ['RL','LL','ECG_DC_BIAS','Generic_LOD_LOW_CHARGE','Sleep - face_DC_BIAS','ECG-1LD','EMG_LL','EMG_RL','Respiratory','Sleep - face','Pulse Oximeter']
    #sensor_names= ['BGX-C1A7','BGX-C1AF','BGX-C161','BGX-C1B0','BGX-C156','BGX-C155','BGX-C15F','O2M 1142','O2M 1111','BGX-C149','BGX-7C1F','BGX-C17D','BGX-C189','BGX-C1DE','BGX-C18D','BGX-C181','BGX-C12E','BGX-C174','BGX-C116','BGX-C152','BGX-C17E','BGX-C12F','BGX-C1A6','BGX-C1DA','BGX-C1A3','BGX-C1AF','BGX-C1A5','BGX-C1A7','BGX-C18C','BGX-C13B','BGX-C162','BGX-C12F','BGX-C154','BGX-7C39','BGX-7C03','BGX-7B7B','BGX-7C20','BGX-7C41','BGX-7CC4','BGX-7C3A','BGX-7C3B','BGX-7CD3','Nonin3150','Nonin3150_506214172']
    #patch_names=['Generic','ECG-1LD','EMG-8ch','Adapter','Sleep-face']

    montages_names=['EMG_LL','EMG_RL']
    sensor_names= []
    patch_names=['EMG-8ch']
    assests_to_assign_dict={'montage_configuration': montages_names,'sensor':sensor_names,'patch':patch_names}
    
    report_name ='test_org_Test2'
    #response = report_mgr.export_full_configuration_snapshot(report_name)
    print('Press Enter When report Created')
    input()
    report_mgr.full_org_transfer_wrapper(manufacturer_id,test_org_id,report_name,assests_to_assign_dict)
