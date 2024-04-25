import re
from pathlib import Path
from file_handler import lines2splits
from constants import VARIATION_MAPPER


def get_variant_monsters(src_monster_txt):
    with open(src_monster_txt, "r") as file:
        monsters = {}
        for sp in lines2splits(file.readlines(), sperator=","):
            match re.sub(r'\d+', "", sp[0]):
                case name if name:
                    if name not in monsters:
                        monsters[name] = {"payload": sp[1:], "alias": [(sp[0], name)]}
                    else:
                        monsters[name]["alias"].append(
                            (sp[0], f"{name}{VARIATION_MAPPER[len(monsters[name]['alias']) + 1]}")
                        )
                case _:
                    continue
        # print(monsters)
    return monsters


if __name__ == "__main__":
    envir_dir = Path(r"D:\MyPlayground\after\Mir200\Envir")
    mon_items_dir = envir_dir / "MonItems"
    mon_gen_pth = envir_dir / "MonGen.txt"

    get_variant_monsters(Path(r"D:\mir\MirServer-RXDF\Mud2\DB\monster.txt"))
