import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
def test_tingwu_api():
    print(f"--- Testing Tingwu API (Beijing) ---")
    ak_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    ak_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    
    from aliyunsdkcore.auth.credentials import AccessKeyCredential
    credentials = AccessKeyCredential(ak_id, ak_secret)
    client = AcsClient(region_id='cn-beijing', credential=credentials)
    
    # This is a GET request to list tasks, which checks if the API key has permission for Tingwu
    request = CommonRequest()
    request.set_domain('tingwu.cn-beijing.aliyuncs.com')
    request.set_version('2023-09-30')
    request.set_method('GET')
    request.set_uri_pattern('/openapi/tingwu/v2/tasks')
    
    try:
        response = client.do_action_with_exception(request)
        print(f"✅ Tingwu API Success: {response.decode('utf-8')}")
    except Exception as e:
        print(f"❌ Tingwu API Failed: {e}")

test_tingwu_api()
