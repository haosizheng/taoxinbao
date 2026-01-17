#!/usr/bin/env python
#coding=utf-8

import os
import json
import datetime
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential

def create_common_request(domain, version, protocolType, method, uri):
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain(domain)
    request.set_version(version)
    request.set_protocol_type(protocolType)
    request.set_method(method)
    request.set_uri_pattern(uri)
    request.add_header('Content-Type', 'application/json')
    return request

def init_parameters():
    body = dict()
    body['AppKey'] = '输入您在听悟管控台创建的Appkey'

    # 基本请求参数
    input = dict()
    input['SourceLanguage'] = 'cn'
    input['TaskKey'] = 'task' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    input['FileUrl'] = '输入待测试的音频url链接'
    body['Input'] = input

    # AI相关参数，按需设置即可
    parameters = dict()

    # 音视频转换相关
    transcoding = dict()
    # 将原音视频文件转成mp3文件，用以后续浏览器播放
    # transcoding['TargetAudioFormat'] = 'mp3'
    # transcoding['SpectrumEnabled'] = False
    # parameters['Transcoding'] = transcoding

    # 语音识别控制相关
    transcription = dict()
    # 角色分离 ： 可选
    transcription['DiarizationEnabled'] = True
    diarization = dict()
    diarization['SpeakerCount'] = 2
    transcription['Diarization'] = diarization
    parameters['Transcription'] = transcription

    # 文本翻译控制相关 ： 可选
    parameters['TranslationEnabled'] = True
    translation = dict()
    translation['TargetLanguages'] = ['en'] # 假设翻译成英文
    parameters['Translation'] = translation

    # 章节速览相关 ： 可选，包括： 标题、议程摘要
    parameters['AutoChaptersEnabled'] = True

    # 智能纪要相关 ： 可选，包括： 待办、关键信息(关键词、重点内容、场景识别)
    parameters['MeetingAssistanceEnabled'] = True
    meetingAssistance = dict()
    meetingAssistance['Types'] = ['Actions', 'KeyInformation']
    parameters['MeetingAssistance'] = meetingAssistance

    # 摘要控制相关 ： 可选，包括： 全文摘要、发言人总结摘要、问答摘要(问答回顾)
    parameters['SummarizationEnabled'] = True
    summarization = dict()
    summarization['Types'] = ['Paragraph', 'Conversational', 'QuestionsAnswering', 'MindMap']
    parameters['Summarization'] = summarization

    # ppt抽取和ppt总结 ： 可选
    parameters['PptExtractionEnabled'] = True
    
    # 口语书面化 ： 可选
    parameters['TextPolishEnabled'] = True
    
    # 大模型后处理任务全局参数 ： 可选
    parameters['Model'] = 'qwq'
    parameters['LlmOutputLanguage'] = 'en'

    body['Parameters'] = parameters
    return body

body = init_parameters()
print(body)

# TODO  请通过环境变量设置您的 AccessKeyId 和 AccessKeySecret
credentials = AccessKeyCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
client = AcsClient(region_id='cn-beijing', credential=credentials)

request = create_common_request('tingwu.cn-beijing.aliyuncs.com', '2023-09-30', 'https', 'PUT', '/openapi/tingwu/v2/tasks')
request.add_query_param('type', 'offline')

request.set_content(json.dumps(body).encode('utf-8'))
response = client.do_action_with_exception(request)
print("response: \n" + json.dumps(json.loads(response), indent=4, ensure_ascii=False))