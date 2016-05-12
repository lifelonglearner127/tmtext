from rest_framework.exceptions import APIException, ParseError


class ParamsCombinationError(APIException):
    status_code = 400
    default_detail = 'The combination of params used is not supported.'


class FormatParseError(ParseError):
    default_detail = 'Date is not valid. Please, make sure you are using'\
                     ' the following format: YYYY-MM-DD'


class ParamNotSupportedError(APIException):
    status_code = 400
