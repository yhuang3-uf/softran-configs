import argparse
import asyncio
import configparser
import io
import pathlib
import sys
import typing

import pycurl

async def make_request(lmf_api_base: str) -> None:
    lmf_api_uri: str = lmf_api_base + "/nlmf-loc/v1/determine-location"
    print(lmf_api_uri)

    async with pycurl.AsyncCurlMulti() as lmf_curl_multi:
        lmf_curl_request: pycurl.Curl = pycurl.Curl()
        lmf_curl_request.setopt(pycurl.URL, lmf_api_uri)
        lmf_curl_request.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_PRIOR_KNOWLEDGE)
        output_bytes_file = io.BytesIO()
        lmf_curl_request.setopt(pycurl.WRITEDATA, output_bytes_file)
        try:
            await lmf_curl_multi.perform(lmf_curl_request)
            print("Server returned HTTP", lmf_curl_request.getinfo(pycurl.RESPONSE_CODE))
            print("Response:")
            print(output_bytes_file.getvalue())
        finally:
            lmf_curl_request.close()

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
    asyncio.run(make_request(lmf_api_base))
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
