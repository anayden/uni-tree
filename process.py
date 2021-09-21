import csv
from dataclasses import dataclass
from typing import Optional, Dict
from itertools import groupby
import hashlib
import logging
from pathlib import Path
from PIL import Image
from resizeimage import resizeimage

import aiohttp
import asyncio

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

@dataclass
class Member:
    name: str
    year: int
    status: str
    parent: Optional[str] = None
    url: Optional[str] = None

    @property
    def hash(self) -> str:
        return "u" + hashlib.sha256(self.name.encode()).hexdigest()[:10]

    @property
    def has_img(self) -> bool:
        return self.url is not None and len(self.url) > 0


member_list = []
members_by_name: Dict[str, Member] = {}

with open("data/members.csv") as csvfile:
    reader = csv.reader(csvfile)
    year = -1
    for row in reader:
        if row[0] == "№":
            year = int(row[1])
        elif row[0] != "":
            _, name, status, parent, _, url, *_ = row
            new_member = Member(name, year, status, parent, url)
            member_list.append(new_member)
            if name in members_by_name:
                print(
                    f"Duplicate member '{name}':\n1. {members_by_name[name]}\n2. {new_member}"
                )
            members_by_name[name] = new_member

with open("data/fixed_members.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    for member in member_list:
        writer.writerow(
            [member.name, member.year, member.status, member.parent, member.url]
        )

unknown = []
for name, data in members_by_name.items():
    if data.parent not in members_by_name:
        unknown.append(data)


async def load_images():
    async with aiohttp.ClientSession() as session:
        for _, data in members_by_name.items():
            if data.has_img:
                try:
                    img_path = Path(f"img/{data.hash}.jpg")
                    if not img_path.exists():
                        async with session.get(data.url) as response:
                            if response.status == 200:
                                img_bytes = await response.read()
                                with open(img_path, 'wb') as f:
                                    f.write(img_bytes)
                                with open(img_path, 'r+b') as f:
                                    with Image.open(f) as image:
                                        resized_image = resizeimage.resize_thumbnail(image, [150, 150]).convert("RGB")
                                        resized_image.save(img_path, image.format)
                except Exception as e:
                    logging.exception("Failed to download a file from '%s'", data.url)


loop = asyncio.get_event_loop()
loop.run_until_complete(load_images())

by_year = groupby(members_by_name.values(), lambda data: data.year)

template = env.get_template('uni.jinja.dot')
with open('output/uni2.dot', 'w') as out:
    rendered = template.render(members=members_by_name, unknown=unknown, by_year=by_year)
    out.write(rendered)

with open("output/uni.dot", "w") as out:
    out.write("digraph uni {\n")
    out.write('root [label="???"]\n')

    for name, data in members_by_name.items():
        label = '<table border="0">'
        if data.has_img:
            label += f'<tr><td width="200" height="200" fixedsize="true"><img src="img/{data.hash}.jpg" scale="true" /></td></tr>'
        label += f"<tr><td>{name}</td></tr>"
        label += f"<tr><td>набор {data.year}</td></tr>"
        label += f"<tr><td>{status}</td></tr>"
        label += "</table>"
        out.write(f"{data.hash} [label=<{label}> shape=box];\n")
        parent = members_by_name.get(data.parent, None)
        parent_hash = parent.hash if parent else "root"
        out.write(f"{parent_hash} -> {data.hash};\n")

    for data in unknown:
        out.write(f'{data.hash} [label="{data.name}"];')

    for year, people in by_year:
        out.write("{ rank=same; \n")
        for data in people:
            out.write(f"{data.hash};\n")
        out.write("}\n")

    out.write("}")
