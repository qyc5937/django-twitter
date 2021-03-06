from rest_framework.response import Response
from rest_framework.status import *
from functools import wraps

def required_params(method='POST', params=None):
    '''
    decorator to check if artribtary number of require params are represent in a request
    '''
    if not params:
        params = []

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, 'query_params' if method == 'GET' else 'data')
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    "message": "missing param(s) {} in request".format(params_str),
                    'success': False,
                }, status=HTTP_400_BAD_REQUEST
                )

            return view_func(instance,request, *args, **kwargs)
        return _wrapped_view
    return decorator