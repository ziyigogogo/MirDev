from pathlib import Path
import shutil
import time

from analyse import get_variant_monsters
from constants import POTIONS
from file_handler import gom1108_mon_items_handler, gom1108_mon_gen_handler


class WorkSpace:
    def __init__(self, src_dir: Path):
        # 读取目录
        src_env_dir = src_dir / "Mir200/Envir"
        src_db_dir = src_dir / "Mud2/DB"
        self.src_mon_items_dir = src_env_dir / "MonItems"
        self.src_monster_txt_pth = src_db_dir / "monster.txt"
        self.src_map_info_pth = src_env_dir / "MapInfo.txt"
        self.src_mon_gen_pth = src_env_dir / "MonGen.txt"
        # 生成目录
        patch_dir = Path(src_dir.stem)
        patch_env_dir = patch_dir / "Mir200/Envir"
        patch_db_dir = patch_dir / "Mud2/DB"
        self.patch_mon_items_dir = patch_env_dir / "MonItems"
        self.patch_monster_txt_pth = patch_db_dir / "monster.txt"
        self.patch_mon_gen_pth = patch_env_dir / r"MonGen.txt"
        shutil.rmtree(patch_dir, ignore_errors=True)
        patch_db_dir.mkdir(parents=True)
        self.patch_mon_items_dir.mkdir(parents=True)


def lines_writer(lines_to_write: list, dst_pth: Path):
    with open(dst_pth, 'w', encoding="ansi") as file:
        file.writelines((x if x.endswith("\n") else f"{x}\n" for x in lines_to_write))


def filter_drop_items(from_dir: Path, to_dir: Path):
    monsters = [gom1108_mon_items_handler(p) for p in from_dir.glob("*.txt")]
    for mon in monsters:
        lines = [f";Edited by Ziyi@{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}"]
        if mon["gold"] > 0:
            lines.extend([f"1/1 金币 {mon['gold']}", f"1/5 金币 {mon['gold'] * 10}"])
        for i in mon["items"]:
            # TODO: 更多物品过滤
            match i[1]:
                case x if x in POTIONS:
                    continue
                case _:
                    lines.append(" ".join(i))
        lines_writer(lines, to_dir / f"{mon['name']}.txt")


def gen_mapper_and_records(monsters: dict):
    mapper, records = {}, []
    for name, data in monsters.items():
        payload = list(map(int, data["payload"]))
        for old_name, new_name in data["alias"]:
            mapper[old_name] = new_name
            # record有22个属性
            records.append(f"{new_name},{','.join(['{:.0f}'] * 21).format(*payload)}")
            """
            0~3: race,race_img,appr, lvl
            4~8: undead, cool_eye, hp, mp, ac
            9~13: mac, dc, dc_max, mc, sc
            14~18: speed, hit, walk_spd, walk_step, walk_wait
            19~20: attack_spd, exp
            """
            payload[6] *= 1.5
            payload[8] *= 1.3
            payload[9] *= 1.3
            payload[10] *= 1.3
            payload[11] *= 1.3
            payload[20] *= 1.5

    return mapper, records


def gen_mon_items(mapper, from_mon_items, to_mon_items):
    # 生成新爆率文件
    for old_name, new_name in mapper.items():
        from_pth = from_mon_items / f"{old_name}.txt"
        to_pth = to_mon_items / f"{new_name}.txt"
        # TODO: 生成对应爆率文件
        if from_pth.exists():
            shutil.copyfile(from_pth, to_pth)
        else:
            print(f"{from_pth.name} not existed, add mon_items file first!")


def gen_mon_gen_txt(mapper, src_mon_gen, patch_mon_gen):
    # TODO:按地图code空行分类
    # TODO:根据怪物星级改变怪物名字颜色
    records = []
    for r in gom1108_mon_gen_handler(src_mon_gen):
        data = [r["code"], r["x"], r["y"], mapper.get(r["mon"], r["mon"]), r["scope"], r["count"], r["interval"]]
        records.append(" ".join(map(str, data)))
    lines_writer(records, patch_mon_gen)


def gen_monster_variation_patch(ws: WorkSpace):
    monster_variations = get_variant_monsters(ws.src_monster_txt_pth)
    mapper, records = gen_mapper_and_records(monster_variations)
    # 生成DBE(PARADOX)数据库导入文件monster.txt
    lines_writer(records, ws.patch_monster_txt_pth)
    # 生成改名后的掉率文件
    gen_mon_items(mapper, ws.src_mon_items_dir, ws.patch_mon_items_dir)
    # 生成改名后的MonGen.txt
    gen_mon_gen_txt(mapper, ws.src_mon_gen_pth, ws.patch_mon_gen_pth)


if __name__ == "__main__":
    gen_monster_variation_patch(WorkSpace(Path(r"D:\mir\MirServer-RXDF")))
