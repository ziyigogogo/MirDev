import re

from pathlib import Path


def lines2splits(lines, sperator=None):
    for line in lines:
        # 去除首尾空格/换行符
        clean_line = line.strip()
        if clean_line and not clean_line.startswith(";"):
            # 去除中间多余空格
            sp = clean_line.split(sperator) if sperator else clean_line.split()
            yield sp


def gom1108_mon_items_handler(pth: Path) -> dict:
    with open(pth, "r") as file:
        formatted_dict = {"name": pth.stem, "gold": 0, "items": []}
        for sp in lines2splits(file.readlines()):
            match len(sp):
                case 2:  # items
                    formatted_dict["items"].append(sp)
                case 3:  # gold
                    formatted_dict["gold"] += int(eval(sp[0]) * eval(sp[2]))
                case _:
                    print(f"error case@<{pth}>: {sp}, ignored.")
    # {'name': '龙神', 'gold': 500, 'items': [['1/5', '龙灵木'], ['1/1', '雪莲']]}
    return formatted_dict


def gom1108_map_info_handler(pth: Path):
    with open(pth, "r") as file:
        code_mapper = {}
        for sp in lines2splits(file.readlines()):
            if sp[0].startswith("["):
                code, name = re.sub(r"\[(.*?)\].*", r"\1", " ".join(sp)).split(" ")[:2]
                code_mapper[code] = name

        return code_mapper


def gom1108_mon_gen_handler(pth: Path) -> list:
    # ;地图代码 x y 怪物名称 范围 数量 时间
    maps = []
    code_mapper = gom1108_map_info_handler(Path(r"D:\mir\MirServer-RXDF\Mir200\Envir\MapInfo.txt"))
    with open(pth, "r") as file:
        for sp in lines2splits(file.readlines()):
            match len(sp):
                case n if n == 7:
                    code, x, y, mon, scope, count, interval = sp[:7]
                    maps.append(
                        {
                            "code": code,
                            "name": code_mapper[code] if code in code_mapper else "UNKNOWN",
                            "x": int(x),
                            "y": int(y),
                            "mon": mon,
                            "scope": int(scope),
                            "count": int(count),
                            "interval": int(interval)
                        }
                    )
                case _:
                    print(f"error: {' '.join(sp)}")
    grouped_maps = sorted(maps, key=lambda row: row["code"])
    return grouped_maps


if __name__ == "__main__":
    envir_dir = Path(r"D:\MyPlayground\before\Mir200\Envir")
    mon_items_dir = envir_dir / "MonItems"
    mon_gen_pth = envir_dir / "MonGen.txt"

    # gom1108_mon_gen_handler(mon_gen_pth)
