import argparse
import asyncio
import configparser
import io
import json
import pathlib
import sys
import typing

import pycurl


class HttpResponse(typing.NamedTuple):
    """
    Represents an HTTP response
    """
    status_code: int
    response: bytes

async def h2_post_data(request_uri: str, data: bytes) -> HttpResponse:
    """
    Sends an HTTP/2 POST request with data

    :param request_uri: The URI to request.
    :param data: The data to request with.
    :return:
    """
    async with pycurl.AsyncCurlMulti() as lmf_curl_multi:
        lmf_curl_request: pycurl.Curl = pycurl.Curl()
        lmf_curl_request.setopt(pycurl.URL, request_uri)
        lmf_curl_request.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_PRIOR_KNOWLEDGE)
        lmf_curl_request.setopt(pycurl.POSTFIELDS, data)
        output_bytes_file = io.BytesIO()
        lmf_curl_request.setopt(pycurl.WRITEDATA, output_bytes_file)
        try:
            await lmf_curl_multi.perform(lmf_curl_request)
            return HttpResponse(
                status_code=lmf_curl_request.getinfo(pycurl.RESPONSE_CODE),
                response=output_bytes_file.getvalue(),
            )
        finally:
            lmf_curl_request.close()

class LmfClient:
    """
    Represents a client that can interface with the LMF
    """
    def __init__(self, api_base: str) -> None:
        self.api_base: str = api_base
        """The base URL of the API (apiBase in 3GPP Technical Standards)"""

    def get_location(self) -> None:
        """
        Makes the request to get the location of a UE
        """
        lmf_api_uri: str = self.api_base + "/nlmf-loc/v1/determine-location"
        location_response = asyncio.run(h2_post_data(
            lmf_api_uri,
            json.dumps({
                "supi": "imsi-208950000000131",
            }).encode("ascii"),
        ))
        print(location_response)


def main(argv: list[str]) -> int:
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="Make requests to the LMF")
    argparser.add_argument("--config-file", "-c", type=pathlib.Path, 
            default=pathlib.Path("lmfclient.ini"),
            help="Path to the configuration file")
    parsedargs: dict[str, typing.Any] = vars(argparser.parse_args(argv[1:]))

    config_file: configparser.ConfigParser = configparser.ConfigParser()
    config_file.read(str(parsedargs["config_file"]))

    lmf_api_base: str = config_file["lmf"]["apibase"]
    lmf_client: LmfClient = LmfClient(lmf_api_base)
    lmf_client.get_location()
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
