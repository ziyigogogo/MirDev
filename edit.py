from pathlib import Path
import shutil
import time

from analyse import get_variant_monsters
from constants import POTIONS
from file_handler import gom1108_mon_items_handler, gom1108_mon_gen_handler, gom1108_map_info_handler


class WorkSpace:
    def __init__(self, from_dir: Path):
        # 读取目录
        from_env_dir = from_dir / "Mir200/Envir"
        from_db_dir = from_dir / "Mud2/DB"
        self.from_mon_items_dir = from_env_dir / "MonItems"
        self.from_monster_txt_pth = from_db_dir / "monster.txt"
        self.from_map_info_pth = from_env_dir / "MapInfo.txt"
        self.from_mon_gen_pth = from_env_dir / "MonGen.txt"
        # 生成目录
        to_dir = Path(from_dir.stem)
        to_env_dir = to_dir / "Mir200/Envir"
        to_db_dir = to_dir / "Mud2/DB"
        self.to_mon_items_dir = to_env_dir / "MonItems"
        self.to_monster_txt_pth = to_db_dir / "monster.txt"
        self.to_mon_gen_pth = to_env_dir / r"MonGen.txt"
        shutil.rmtree(to_dir, ignore_errors=True)
        to_db_dir.mkdir(parents=True)
        self.to_mon_items_dir.mkdir(parents=True)


def lines_writer(lines_to_write: list, to_pth: Path):
    with open(to_pth, "w", encoding="ansi") as file:
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
            payload[6] *= 1.5  # 血量
            payload[8] *= 1.3  # 物防
            payload[9] *= 1.3  # 魔防
            payload[10] *= 1.3  # 攻击下限
            payload[11] *= 1.3  # 攻击上限
            payload[20] *= 1.5  # 经验值

    return mapper, records


def gen_mon_items(mapper, from_mon_items, to_mon_items):
    # 生成新爆率文件
    for old_name, new_name in mapper.items():
        from_pth = from_mon_items / f"{old_name}.txt"
        to_pth = to_mon_items / f"{new_name}.txt"
        # TODO: 从template生成对应爆率文件
        try:
            shutil.copyfile(from_pth, to_pth)
        except FileNotFoundError:
            to_pth.touch()
            print(f"{from_pth.name} not existed, created an empty file: {to_pth.absolute()}")


def gen_mon_gen_txt(mon_mapper, from_mon_gen, to_mon_gen):
    # TODO:根据怪物星级改变怪物名字颜色
    records = [";地图代码 x y 怪物名称 范围 数量 时间"]
    map_name = None
    for r in gom1108_mon_gen_handler(from_mon_gen):
        cur_map = r.pop("map")
        if map_name != cur_map:
            records.append(f"\n;{cur_map}" if map_name else f";{cur_map}")
            map_name = cur_map
        r["mon"] = mon_mapper.get(r["mon"], r["mon"])
        records.append(" ".join(map(str, r.values())))
    lines_writer(records, to_mon_gen)


def gen_monster_variation_patch(ws: WorkSpace):
    monster_variations = get_variant_monsters(ws.from_monster_txt_pth)
    mon_mapper, records = gen_mapper_and_records(monster_variations)

    # 生成DBE(PARADOX)数据库导入文件monster.txt
    lines_writer(records, ws.to_monster_txt_pth)

    # 生成改名后的掉率文件
    gen_mon_items(mon_mapper, ws.from_mon_items_dir, ws.to_mon_items_dir)

    # 生成改名后的MonGen.txt
    gen_mon_gen_txt(mon_mapper, ws.from_mon_gen_pth, ws.to_mon_gen_pth)


if __name__ == "__main__":
    gen_monster_variation_patch(WorkSpace(Path(r"D:\mir\MirServer-RXDF")))
