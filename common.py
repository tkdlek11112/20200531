from enum import Enum

OK = 0
BAD_INPUT = 1
DATA_ERROR = 2

NO_LANGUAGE = 1001
NO_SUPPORT_LANGUAGE = 1002
REQ_COUNT_ERROR = 2001

NO_TAG = 3001
NO_COMPANY = 3002



code_msg = {
    OK: "done",
    BAD_INPUT: "bad request parameter",
    DATA_ERROR: "unknown data error",
    NO_LANGUAGE: "no input language",
    NO_SUPPORT_LANGUAGE: "no support language",
    REQ_COUNT_ERROR: "bad input count",
    NO_TAG: "don't find tag",
    NO_COMPANY: "don't find company",

}
LANG_KOR = "ko"
LANG_ENG = "en"
LANG_JPN = "jp"

LANG_LIST = [
    LANG_KOR,
    LANG_ENG,
    LANG_JPN
]

def ret_api(code):
    return {'code': code, 'msg': code_msg[code]}


def ret_api_data(code, data):
    return {'code': code, 'msg': code_msg[code], 'data': data}
