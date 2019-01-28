#!/usr/bin/env python3

from os import environ

from requests import delete, get, post, put


def call(
        uri,
        request_data=None,
        method='GET',
        only_response_code=False,
        rest_url=environ.get('TFS_REST_URL', None),
        token=environ.get('TFS_TOKEN', None),
):
    """Makes a REST call to TFS rest api.
    May use three environment variables:
    * TFS_REST_URL, e.g. http://myorg.com/stash
    * TFS_TOKEN, the tfs token

    Args:
        uri (str): e.g. "/rest/api/1.0/projects/{project}/repos/{repo}/branches?filterText={branch}"
        request_data (dict): the JSON request
        method: http method
        only_response_code: default False
        rest_url: default environ.get('TFS_REST_URL', None)
        token: default environ.get('TFS_TOKEN', None),

    Return:
          the JSON response
    """
    m = {'DELETE': delete,
         'GET': get,
         'POST': post,
         'PUT': put,
         }[method]

    response = m(url=f'{rest_url}{uri}', json=request_data or '', auth=('', token))
    return response.status_code if only_response_code else response.json()
