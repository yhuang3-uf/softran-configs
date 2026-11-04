import argparse
import configparser
import pathlib
import sys
import typing

import httpx

def main(argv: list[str]) -> int:
    argparser: argparse.ArgumentParser = argpaser.ArgumentParser(
            description="Make requests to the LMF")
    argparser.add_argument("--config-file", "-c", type=pathlib.Path, 
            default=pathlib.Path("lmfclient.py"),
            help="Path to the configuration file")
    parsedargs: dict[str, typing.Any] = vars(argparser.parse_args(argv[1:]))

    config_file: configparser.ConfigParser = configparser.ConfigParser()
    config_file.read(str(parsedargs["config_file"]))

    lmf_api_base: str = config_file["lmf"]["apibase"]
    async with httpx.AsyncClient(http2=True) as lmf_session:
        lmf_result: httpx.Response = await lmf_session.post(
            lmf_api_base + "/nlmf-loc/v1/determine-location",
            json={
                "supi": "imsi-208950000000131",
            },
        )
        print(f"Got HTTP {lmf_result.status_code}")
        print(lmf_result.text)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
