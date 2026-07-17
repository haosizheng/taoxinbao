import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json

def get_token(region):
    print(f"--- Attempting Token in {region} ---")
    ak_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    ak_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    
    client = AcsClient(ak_id, ak_secret, region)
    request = CommonRequest()
    request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
    request.set_version("2019-02-28")
    request.set_action_name("CreateToken")
    request.set_protocol_type('https')
    
    try:
        response = client.do_action_with_exception(request)
        print(f"Success in {region}: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Failed in {region}: {e}")

# The Token API endpoint is usually global at Shanghai, 
# but the client region can sometimes affect authentication.
get_token("cn-shanghai")
get_token("cn-beijing")
