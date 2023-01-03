from CONST import *
import pprint

# pp = pprint.PrettyPrinter(indent=4)

def get_tooltip(id):
    lst = [value for value in DICT_TALENT.values() if value['group_id'] == id]
    name = DICT_KOREAN[lst[0]['name_id']]
    if lst[0]["isSkill"]:
        name += "(스킬)"
    texts = []
    for value in lst:
        desc_string = DICT_KOREAN[value['desc_id']]
        for idx, des_value in enumerate(value['des_value']):
            desc_string = desc_string.replace(f"{{{idx}}}", des_value)
        text = f"Lv.{value['Lv']} {desc_string}"
        texts.append(text)

    return name, texts


def get_desc_ids(id, Lv):
    value = [value for value in DICT_TALENT.values() if (value['group_id'] == id) and (value['Lv'] == Lv)][0]
    desc_id = value['desc_id']
    desc_value = value['des_value']
    return desc_id, desc_value

def get_desc_value():
    pass

# def make_home_desc_text():
