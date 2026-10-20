"""Read the matching official desktop release's settings and embed them in the build."""
import argparse
import base64
import os
import pathlib
import re
import uuid
import zipfile

import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes


SOURCE = pathlib.Path("Plain Craft Launcher 2/Modules/ModSecret.vb")


def constants(pe, type_name):
    types = [t for t in pe.net.mdtables.TypeDef
             if str(t.TypeNamespace) == "PCL" and str(t.TypeName) == type_name]
    if len(types) != 1:
        raise RuntimeError(f"Expected exactly one PCL.{type_name} type.")
    fields = {f.row_index: str(f.row.Name) for f in types[0].FieldList}
    return {
        fields[c.Parent.row_index]: c.Value.value
        for c in pe.net.mdtables.Constant
        if c.Parent.table.name == "Field" and c.Parent.row_index in fields
    }


def official_settings(tag):
    with zipfile.ZipFile("最新正式版.zip") as archive:
        data = archive.read("Plain Craft Launcher 2.exe")
    pe = dnfile.dnPE(data=data)
    version = constants(pe, "ModBase")["VersionBaseName"].decode("utf-16-le")
    if version != tag.removeprefix("v"):
        raise RuntimeError("The bundled official executable does not match the upstream tag.")
    client_id = constants(pe, "ModSecret")["OAuthClientId"].decode("utf-16-le")
    uuid.UUID(client_id)
    secret_type = next(t for t in pe.net.mdtables.TypeDef if str(t.TypeName) == "ModSecret")
    methods = [m.row for m in secret_type.MethodList if str(m.row.Name) == "SecretHeadersSign"]
    if len(methods) != 1:
        raise RuntimeError("The official header routine has changed.")
    body = CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(methods[0].Rva)))
    strings = [pe.net.user_strings.get(i.operand.rid).value
               for i in body.instructions if str(i.opcode) == "ldstr"]
    positions = [i for i, value in enumerate(strings) if value == "x-api-key"]
    if len(positions) != 1 or positions[0] + 2 != len(strings):
        raise RuntimeError("The official API header layout has changed.")
    api_key = base64.b64decode(strings[positions[0] + 1], validate=True).decode("ascii")
    if not re.fullmatch(r"\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}", api_key):
        raise RuntimeError("The official API credential format has changed.")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for value in (client_id, api_key):
            print(f"::add-mask::{value}")
    return {"OAuthClientId": client_id, "CurseForgeAPIKey": api_key}


def embed(settings):
    source = SOURCE.read_bytes()
    for name, value in settings.items():
        pattern = (
            rb'Public ' + name.encode() +
            rb' As String = If\(Environment\.GetEnvironmentVariable\("PCL_[A-Z_]+"\), ""\)'
        )
        replacement = f'Public Const {name} As String = "{value}"'.encode()
        source, count = re.subn(pattern, lambda _: replacement, source)
        if count != 1:
            raise RuntimeError(f"Expected exactly one unmodified {name} declaration.")
    if b"Public Const RestrictMcDownload As Boolean = False" not in source:
        raise RuntimeError("The requested download patch is missing.")
    SOURCE.write_bytes(source)
    print("Embedded both official settings; runtime environment variables are not used.")


def verify(settings, executable):
    data = pathlib.Path(executable).read_bytes()
    pe = dnfile.dnPE(data=data)
    values = constants(pe, "ModSecret")
    for name, expected in settings.items():
        if values.get(name) != expected.encode("utf-16-le"):
            raise RuntimeError(f"The compiled {name} does not match the official release.")
    if values.get("RestrictMcDownload") != b"\x00":
        raise RuntimeError("The compiled download restriction is not disabled.")
    for name in ("PCL_MS_CLIENT_ID", "PCL_CURSEFORGE_API_KEY"):
        if name.encode("utf-16-le") in data:
            raise RuntimeError("A runtime environment-variable lookup remains in the executable.")
    print("Verified compiled settings match the official release, restriction is False, and environment lookups are absent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["embed", "verify"])
    parser.add_argument("--tag", default=os.environ.get("UPSTREAM_TAG"), required=False)
    parser.add_argument("--exe", default="Plain Craft Launcher 2/bin/Plain Craft Launcher 2.exe")
    args = parser.parse_args()
    if not args.tag:
        parser.error("--tag or UPSTREAM_TAG is required")
    settings = official_settings(args.tag)
    if args.mode == "embed":
        embed(settings)
    else:
        verify(settings, args.exe)
