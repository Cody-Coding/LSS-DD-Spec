import dearpygui.dearpygui as dpg
from CONST import *
from utils import *
from math import sin, cos, atan2, pi
import pickle
import pprint

pp = pprint.PrettyPrinter(indent=4)
PATH_FONT_BD = "fonts\\NanumSquareNeo-cBd.ttf"

# PATH_FONT_BD = "fonts\\GmarketSansTTFMedium.ttf"
# PATH_FONT_BD = "fonts\\GmarketSansTTFBold.ttf"
# PATH_FONT_BD = "fonts\\NanumSquareNeo-bRg.ttf"
# PATH_FONT_HV = "fonts\\NanumSquareNeo-eHv.ttf"
PATH_SAVE = "data.bin"
PATH_ICON = "resource\\icon.ico"

class App:
    __index_DD = 0
    BTN_BORDER_SIZE = 4

    def __init__(self) -> None:
        dpg.create_context()

    def __cb_load_data_file(self):
        dpg.hide_item("load_window")
        list_values = [dpg.get_value(id) for id in dpg.get_item_children("list_checkbox_load", 1)]

        with open(PATH_SAVE, "rb") as f:
            dic_load = pickle.load(f)

        list_data_to_load = [dict_data for value, dict_data in zip(list_values, dic_load.values()) if value]
        for dict_data in list_data_to_load:
            self.__load_data(dict_data)

        # pp.pprint(list_tabid_to_load)

    def __cb_save_data_file(self):
        list_tabs = [dpg.get_item_alias(id) for id in dpg.get_item_children("DD_set_tab_bar", 1) if (dpg.get_item_type(id) == "mvAppItemType::mvTab")]
        list_values = [dpg.get_value(id) for id in dpg.get_item_children("list_checkbox_save", 1)]
        # print(list_values)
        dpg.hide_item("save_window")
        if not any(list_values):
            pass
        else:
            list_tabid_to_save = [tab_id for value, tab_id in zip(list_values, list_tabs) if value] 
            dic_save = {}
            """딕셔너리 구조"""
            # key : index
            # value : dict - Key{HomeId, 'tab_user_data}
            for idx, item_id in enumerate(list_tabid_to_save):
                tab_tag = dpg.get_item_alias(item_id)
                dic ={}
                dic.update({'tab_label': dpg.get_item_label(tab_tag)})
                dic.update({'tab_user_data': dpg.get_item_user_data(tab_tag)})
                for HomeId in DICT_HOME:
                    group_tag = f"{tab_tag}_G{HomeId}"
                    lst_child_id = dpg.get_item_children(group_tag, 1)
                    lst_user_data = [dpg.get_item_user_data(id) for id in lst_child_id if dpg.get_item_type(id) == "mvAppItemType::mvButton"]
                    dic_user_data = {user_data['id']: user_data['currentLv'] for user_data in lst_user_data if user_data['currentLv'] != 0}
                    dic.update({HomeId : dic_user_data})
                dic_save[idx] = dic
            with open(PATH_SAVE, "wb") as f:
                pickle.dump(dic_save, f)
            # dpg.hide_item("save_window")

    def __cb_open_load_window(self):
        try:
            with open(PATH_SAVE, "rb") as f:
                dic_load = pickle.load(f)
            lst_label = [value['tab_label'] for value in dic_load.values()]
            # print(lst_label)
            # list_checkbox_load
            dpg.delete_item("list_checkbox_load", children_only=True)
            for label in lst_label:
                dpg.add_checkbox(label=label, parent="list_checkbox_load")
            dpg.set_item_height("load_window", -1)
            dpg.show_item("load_window")
            dpg.focus_item("load_window")
        except:
            print("No save file")

    def __cb_input_DD_set_name(self):
        with dpg.window(label="탭 추가하기", modal=True, tag="modal_input_name", on_close=self.__cb_delete_on_close, no_resize=True, pos=(600,400) ):
            # dpg.add_text("이름을 입력하세요.")
            dpg.add_text("한글이 깨질 경우 붙여넣기를 사용하세요.")
            dpg.add_spacer()
            dpg.add_input_text(label="", width=-1, hint="이름을 입력하세요." ,tag="input_name", on_enter=True, callback=self._cb_name_enter)
            dpg.focus_item(dpg.last_item())
            # dpg.bind_item_font(dpg.last_item(), "font_bold")
            dpg.add_button(label="추가", width=-1, callback=self.__cb_name_add_button)
    
    def __cb_name_add_button(self, sender, app_data, user_data):
        value = dpg.get_value("input_name")
        dpg.delete_item("modal_input_name")
        if value == "":
            tag = self.__add_DD_tab()
        else:
            tag = self.__add_DD_tab(value)
        # dpg.focus_item(tag)
        # print(tag)
        return value

    def _cb_name_enter(self, sender, app_data, user_data):
        dpg.delete_item("modal_input_name")
        if app_data == "":
            self.__add_DD_tab()
        else:
            self.__add_DD_tab(app_data)
        return app_data

    def __cb_delete_on_close(self, sender):
        dpg.delete_item(sender)
    
    def __cb_delete_parent(self, sender):
        dpg.delete_item(dpg.get_item_parent(sender))


    def __cb_hide_on_close(self, sender):
        dpg.hide_item(sender)
        # dpg.setitem

    def __cb_open_save_window(self, sender, app_data, user_data):
        self.__update_save_list()
        dpg.show_item("save_window")
        dpg.focus_item("save_window")
        
    def __cb_reset(self, sender, app_data, user_data):
        parent = dpg.get_item_parent(sender)
        set_tag = parent.split('_')[0]
        set_user_data = dpg.get_item_user_data(set_tag)
        home_tag = parent.replace('G', 'T')
        home_user_data = dpg.get_item_user_data(home_tag)
        set_user_data['Pt'] -= home_user_data['Pt']
        home_user_data['Pt'] = 0

        dpg.set_item_user_data(set_tag, set_user_data)
        dpg.set_item_label(set_tag, set_user_data['text'].replace("{0}", str(set_user_data['Pt'])))
        
        dpg.set_item_user_data(home_tag, home_user_data)
        dpg.set_item_label(home_tag, home_user_data['text'].replace("{0}", str(home_user_data['Pt'])))
        HomeId = int(parent.split('_')[1][1:])
        lst_id = [key for key, value in DICT_CONNECT.items() if (value['HomeId'] == HomeId) and (key != user_data['id'])]
        for id in lst_id:
            button_tag = f"{parent}_B{id}"
            button_user_data = {'id': id, 'currentLv': 0}
            theme_tag = '_'.join(dpg.get_item_theme(button_tag).split('_')[:-1]) + '_zero'

            dpg.set_item_label(button_tag, button_user_data["currentLv"])
            dpg.set_item_user_data(button_tag, button_user_data)
            dpg.bind_item_theme(button_tag, theme_tag)


    def __cb_DD_button(self, sender, app_data, user_data):
        parent = dpg.get_item_parent(sender)
        set_tag = parent.split('_')[0]
        set_user_data = dpg.get_item_user_data(set_tag)
        home_tag = parent.replace('G', 'T')
        home_user_data = dpg.get_item_user_data(home_tag)
        maxLv = DICT_CONNECT[user_data["id"]]["maxLv"]
        if user_data["currentLv"] < maxLv:
            if self.__check_needTalent(user_data["id"], dpg.get_item_parent(sender)):
                user_data["currentLv"] += 1
                set_user_data['Pt'] += 1
                home_user_data['Pt'] += 1
        else:
            if self.__check_nextTalent(user_data["id"], dpg.get_item_parent(sender)):
                user_data["currentLv"] = 0
                set_user_data['Pt'] -= maxLv
                home_user_data['Pt'] -= maxLv
        
        dpg.set_item_user_data(set_tag, set_user_data)
        dpg.set_item_label(set_tag, set_user_data['text'].replace("{0}", str(set_user_data['Pt'])))
        
        dpg.set_item_user_data(home_tag, home_user_data)
        dpg.set_item_label(home_tag, home_user_data['text'].replace("{0}", str(home_user_data['Pt'])))

        dpg.set_item_label(sender, user_data["currentLv"])
        dpg.set_item_user_data(sender, user_data)
        HomeId = DICT_CONNECT[user_data["id"]]["HomeId"]
        size = DICT_CONNECT[user_data["id"]]["size"]
        if user_data["currentLv"] == 0:
            theme_tag = f"theme_btn_{HomeId}_{size}_zero"
        else:
            theme_tag = f"theme_btn_{HomeId}_{size}_nonzero"
        dpg.bind_item_theme(sender, theme_tag)

        self.__update_desc_summary(dpg.get_item_parent(sender))

    def __setup(self) -> None:
        # 폰트 등록
        with dpg.font_registry():
            # with dpg.font(PATH_FONT_RG, 16, tag="font_regular"):
            #     dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            #     dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

            with dpg.font(PATH_FONT_BD, 16, tag="font_bold"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                # dpg.add_font_range(0x1100, 0x11FF)
                # dpg.add_font_range(0x3130, 0x318F)
                # dpg.add_font_range(0xA960, 0xA97F)
                # dpg.add_font_range(0xAC00, 0xD7AF)
                # dpg.add_font_range(0xD7B0, 0xD7FF)

            # with dpg.font(PATH_FONT_BD, 16, tag="font_heavy"):
            #     dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            #     dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)


        # 기본 폰트 설정
        dpg.bind_font("font_bold")
        # 버튼 크기
        SET_BTN_SIZE = set([value["size"] for value in DICT_CONNECT.values()])

        for HomeId in DICT_HOME:
            # 탭 색깔
            theme_tag = f"theme_tab_{HomeId}"
            with dpg.theme(tag=theme_tag):
                with dpg.theme_component(dpg.mvTab):
                    dpg.add_theme_color(dpg.mvThemeCol_Tab, DICT_HOME[HomeId]["rgb3"])
                    dpg.add_theme_color(
                        dpg.mvThemeCol_TabActive, DICT_HOME[HomeId]["rgb1"]
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_TabHovered, DICT_HOME[HomeId]["rgb2"]
                    )

                    # 전념 버튼
            for size in SET_BTN_SIZE:
                theme_tag = f"theme_btn_{HomeId}_{size}_zero"
                # ZERO
                with dpg.theme(tag=theme_tag):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, size / 2)
                        dpg.add_theme_style(
                            dpg.mvStyleVar_FrameBorderSize, self.BTN_BORDER_SIZE
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_ButtonActive, DICT_HOME[HomeId]["rgb3"]
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_ButtonHovered, DICT_HOME[HomeId]["rgb2"]
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_Border, DICT_HOME[HomeId]["rgb2"]
                        )

                # NONZERO
                theme_tag = f"theme_btn_{HomeId}_{size}_nonzero"
                with dpg.theme(tag=theme_tag):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, size / 2)
                        dpg.add_theme_style(
                            dpg.mvStyleVar_FrameBorderSize, self.BTN_BORDER_SIZE
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_Button, DICT_HOME[HomeId]["rgb1"]
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_ButtonActive, DICT_HOME[HomeId]["rgb3"]
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_ButtonHovered, DICT_HOME[HomeId]["rgb2"]
                        )
                        dpg.add_theme_color(
                            dpg.mvThemeCol_Border, DICT_HOME[HomeId]["rgb2"]
                        )


    def __init_DD_window(self) -> None:
        with dpg.window(label="Main Window", width=1550, height=850, tag="main_window"):
            with dpg.tab_bar(tag="DD_set_tab_bar"):
                dpg.add_tab_button(label="+", trailing=True, tag="DD_set_add_button", callback=self.__cb_input_DD_set_name)
                # dpg.bind_item_font("DD_set_add_button", "font_heavy")
                dpg.add_tab_button(
                    label="저장하기", trailing=True, tag="DD_set_save_button", callback=self.__cb_open_save_window
                )
                # dpg.bind_item_font("DD_set_save_button", "font_heavy")
                dpg.add_tab_button(
                    label="불러오기", trailing=True, tag="DD_set_load_button", callback=self.__cb_open_load_window
                )
                # dpg.bind_item_font("DD_set_load_button", "font_heavy")
        dpg.set_primary_window("main_window", True)
    """말세 전념 관련 함수"""

    def __add_DD_tab(self, set_name="전념탭", show=True) -> None:
        """탭추가"""
        self.__index_DD += 1
        set_tag = f"S{self.__index_DD}"
        set_name += str(self.__index_DD) if set_name == "전념탭" else ""
        set_user_data = {'text' : f"{set_name} ({{{0}}})", 'Pt': 0}
        set_label = f"{set_name} ({set_user_data['Pt']})"
        with dpg.tab(label=set_label, parent="DD_set_tab_bar", user_data=set_user_data, tag=set_tag, show=show, closable=True):
            dpg.add_spacer()
            with dpg.tab_bar():
                for HomeId, value in DICT_HOME.items():
                    home_label = f"{value['name']} (0)"
                    home_tag = f"S{self.__index_DD}_T{HomeId}"
                    home_user_data = {'text': f"{value['name']} ({{{0}}})", 'Pt': 0}
                    theme_tag = f"theme_tab_{HomeId}"
                    with dpg.tab(label=home_label, user_data=home_user_data, tag=home_tag):
                        # dpg.bind_item_font(dpg.last_item(), "font_bold")
                        dpg.bind_item_theme(dpg.last_item(), theme_tag)
                        with dpg.child_window(horizontal_scrollbar=True):
                            self.__add_DD_buttons(self.__index_DD, HomeId)
                            self.__draw_connect(HomeId)
                            dpg.add_spacer(height=4)
                            dpg.add_collapsing_header(
                                label="요약", tag=f"S{self.__index_DD}_I{HomeId}"
                            )

        return set_tag
        # dpg.bind_item_font(set_tag, "font_heavy")
        # dpg.show_item(set_tag)

    def __add_DD_buttons(self, index, HomeId) -> None:
        dic = {
            id: value for id, value in DICT_CONNECT.items() if value["HomeId"] == HomeId
        }
        group_tag = f"S{index}_G{HomeId}"
        with dpg.group(tag=group_tag, pos=(0, 0)):
            for id, value in dic.items():
                pos = (value["x"] + 8, value["y"] + 8)
                button_tag = f"S{index}_G{HomeId}_B{id}"
                button_theme_tag = f"theme_btn_{HomeId}_{value['size']}_zero"
                user_data = {"id": id, "currentLv": 0}
                # 리셋버튼 조건문
                if value["default"]:
                    dpg.add_button(
                        label="리셋",
                        width=value["size"],
                        height=value["size"],
                        pos=pos,
                        user_data=user_data,
                        tag=button_tag,
                        callback=self.__cb_reset
                    )
                    with dpg.tooltip(parent=button_tag):
                        dpg.add_text("전념초기화")
                        # dpg.bind_item_font(dpg.last_item(), "font_heavy")
                else:
                    dpg.add_button(
                        label='0',
                        width=value["size"],
                        height=value["size"],
                        pos=pos,
                        user_data=user_data,
                        tag=button_tag,
                        callback=self.__cb_DD_button,
                    )
                    with dpg.tooltip(parent=button_tag):
                        name, desc = get_tooltip(id)
                        dpg.add_text(name)
                        # dpg.bind_item_font(dpg.last_item(), "font_bold")
                        dpg.add_spacer()
                        for text in desc:
                            dpg.add_text(text)
                            # dpg.bind_item_font(dpg.last_item(), "font_regular")

                dpg.bind_item_theme(button_tag, button_theme_tag)
                # dpg.bind_item_font(button_tag, "font_heavy")
                # 버튼 폰트

    def __draw_connect(self, HomeId) -> None:
        dic = {
            id: value for id, value in DICT_CONNECT.items() if value["HomeId"] == HomeId
        }
        width = max(value["x"] + value["size"] for value in dic.values())
        height = max(value["y"] + value["size"] for value in dic.values())
        with dpg.drawlist(width=width, height=height):
            for value in dic.values():
                circle1 = (value["x"], value["y"], value["size"])
                for talent in value["needTalent"]:
                    talent_id = int(talent.split("_")[0])
                    circle2 = (
                        dic[talent_id]["x"],
                        dic[talent_id]["y"],
                        dic[talent_id]["size"],
                    )
                    p1, p2 = self.__get_line_pos(circle1, circle2)
                    dpg.draw_line(p1, p2, thickness=4, color=DICT_HOME[HomeId]["rgb2"])

    def __get_line_pos(self, circle1, circle2):
        size1 = circle1[2]
        size2 = circle2[2]
        x1, y1 = circle1[0] + size1 / 2, circle1[1] + size1 / 2
        x2, y2 = circle2[0] + size2 / 2, circle2[1] + size2 / 2
        x = x1 - x2
        y = y1 - y2
        theta = atan2(y, x)
        start_p = x1 + (size1 + self.BTN_BORDER_SIZE) / 2 * cos(theta + pi), y1 + (
            size1 + self.BTN_BORDER_SIZE
        ) / 2 * sin(theta + pi)
        end_p = x2 + (size2 + self.BTN_BORDER_SIZE) / 2 * cos(theta), y2 + (
            size2 + self.BTN_BORDER_SIZE
        ) / 2 * sin(theta)
        return (start_p, end_p)

    def __check_needTalent(self, id, parent):
        needTalent = DICT_CONNECT[id]["needTalent"]
        if not needTalent:
            return False

        needTalent_tag = [f"{parent}_B{talent.split('_')[0]}" for talent in needTalent]
        needTalent_Lv = [int(talent.split("_")[1]) for talent in needTalent]
        currentLv = [dpg.get_item_user_data(tag)["currentLv"] for tag in needTalent_tag]
        result = True in [
            need == current for need, current in zip(needTalent_Lv, currentLv)
        ]
        return result

    def __check_nextTalent(self, id, parent):
        nextTalent = DICT_CONNECT[id]["nextTalent"]
        if not nextTalent:
            return True

        nextTalent_tag = [f"{parent}_B{talent_id}" for talent_id in nextTalent]
        sum_currentLv = sum(
            dpg.get_item_user_data(tag)["currentLv"] for tag in nextTalent_tag
        )
        if sum_currentLv == 0:
            return True
        return False

    def __update_desc_summary(self, parent):
        summary_tag = parent.replace("G", "I")
        dpg.delete_item(summary_tag, children_only=True, slot=1)
        texts = self.__get_desc_string(parent)
        for text in texts:
            dpg.add_text(text, bullet=True, parent=summary_tag)

    def __get_desc_string(self, parent):
        desc_string = []
        desc_skill = []
        lst_connect_id = [
            key
            for key, value in DICT_CONNECT.items()
            if value["HomeId"] == int(parent.split("_")[1][-3:])
        ]
        lst_desc = []
        for connect_id in lst_connect_id:
            user_data = dpg.get_item_user_data(f"{parent}_B{connect_id}")
            if user_data["currentLv"] != 0:
                lst = [
                    (
                        value["name_id"],
                        value["desc_id"],
                        value["isSkill"],
                        value["des_value"],
                    )
                    for value in DICT_TALENT.values()
                    if (value["group_id"] == user_data["id"])
                    and (value["Lv"] == user_data["currentLv"])
                ]
                lst_desc.extend(lst)

        for desc in set(item[:3] for item in lst_desc):
            if desc[2]:
                text = f"{DICT_KOREAN[desc[0]]}(스킬) : {DICT_KOREAN[desc[1]]}"
            else:
                text = f"{DICT_KOREAN[desc[0]]} : {DICT_KOREAN[desc[1]]}"

            lst_values = [item[3] for item in lst_desc if item[:3] == desc]
            # 첫번째 값의 길이로 구분
            if len(lst_values) == 1:
                for i, v in enumerate(lst_values[0]):
                    text = text.replace(f"{{{i}}}", v)
            else:
                if lst_values[0][0].isdigit():  # 양수
                    if desc[0] == 90602144:  # 토지개발
                        # print("토지개발")
                        max_value = max(int(value[0]) for value in lst_values)
                        text = text.replace("{0}", str(max_value))
                    else:  # 나머지 경우(일반)
                        # print("양수일반")
                        sum_value = sum(int(value[0]) for value in lst_values)
                        text = text.replace("{0}", str(sum_value))

                elif "-" in lst_values[0][0]:  # 음수
                    # print("음수일반")
                    sum_value = -1 * sum(int(value[0][1:]) for value in lst_values)
                    text = text.replace("{0}", str(sum_value))
            # 조건문 스킬과 일반 구분
            if desc[2]:
                desc_skill.append(text)
            else:
                desc_string.append(text)
        desc_string.extend(desc_skill)
        return desc_string

    def __add_save_window(self):
        pos = ((1600-200)/2, 300)
        with dpg.window(tag="save_window",pos=pos, width=200, height=-1, max_size=(400, 500), modal=True, show=False, no_collapse=True, no_resize=True, on_close=self.__cb_hide_on_close):
            dpg.add_text("저장할 항목을 선택하세요.")
            dpg.add_spacer()
            with dpg.group(tag="list_checkbox_save", parent="save_window"):
                pass
            dpg.add_spacer()
            dpg.add_button(label="저장", width=-1, callback=self.__cb_save_data_file)
            
    def __update_save_list(self):
        #숨겨진 탭 삭제
        lst_hide = [id for id in dpg.get_item_children("DD_set_tab_bar", 1) if not dpg.is_item_shown(id)]
        for item in lst_hide:
            dpg.delete_item(item)
        lst_item = [item for item in dpg.get_item_children("DD_set_tab_bar", 1) if (dpg.get_item_type(item) == "mvAppItemType::mvTab")]
        dpg.delete_item('list_checkbox_save', children_only=True)
        for item in lst_item:
            dpg.add_checkbox(label=dpg.get_item_label(item), parent="list_checkbox_save")
        dpg.set_item_height("save_window", -1)

    def __add_load_window(self):
        pos = ((1600-200)/2, 300)
        with dpg.window(tag="load_window", pos=pos, width=200, max_size=(400, 500), height=-1, modal=True, show=False, no_collapse=True, no_resize=True, on_close=self.__cb_hide_on_close):
            dpg.add_text("불러올 항목을 선택하세요.")
            dpg.add_spacer()
            with dpg.group(tag="list_checkbox_load", parent="load_window"):
                pass
            dpg.add_spacer()
            dpg.add_button(label="불러오기", width=-1, callback=self.__cb_load_data_file)

    def __update_load_list(self):
        with open(PATH_SAVE, "rb") as f:
            dic_load = pickle.load(f)
        lst_label = [value['tab_label'] for value in dic_load.values()]
     
        dpg.delete_item('list_checkbox_load', children_only=True)
        for item in lst_label:
            dpg.add_checkbox(label=dpg.get_item_label(item), parent="list_checkbox_load")
        dpg.set_item_height("load_window", -1)

    def __load_data(self, dict_data):
        # pp.pprint(dict_data)
        tab_label = dict_data['tab_label']
        tab_user_data = dict_data['tab_user_data']
        set_tag = self.__add_DD_tab(show=False)
        dpg.set_item_label(set_tag, tab_label)
        dpg.set_item_user_data(set_tag, tab_user_data)
        for HomeId in DICT_HOME:
            home_tag = f"{set_tag}_T{HomeId}"
            home_user_data = dpg.get_item_user_data(home_tag)
            sum_Pt = 0
            for id, Lv in dict_data[HomeId].items():
                button_tag = f"{set_tag}_G{HomeId}_B{id}"
                dpg.set_item_label(button_tag, str(Lv))
                dpg.set_item_user_data(button_tag, {'id': id, 'currentLv': Lv})
                dpg.bind_item_theme(button_tag, dpg.get_item_theme(button_tag).replace("zero", "nonzero"))
                sum_Pt += Lv
            home_user_data['Pt'] = sum_Pt
            home_label = home_user_data['text'].replace("{0}", str(sum_Pt))
            dpg.set_item_label(home_tag, home_label)
            dpg.set_item_user_data(home_tag, home_user_data)
            self.__update_desc_summary(f"{set_tag}_G{HomeId}")
        #버튼 업데이트
        dpg.show_item(set_tag)


    def run(self) -> None:
        dpg.setup_dearpygui()

        self.__setup()
        self.__init_DD_window()
        self.__add_save_window()
        self.__add_load_window()
        # self.__add_DD_tab()
        dpg.create_viewport(title="I'M READY TO RETIRE NOW. DO YOU WANT TO JOIN ME? :)", width=1600, height=900, small_icon=PATH_ICON, large_icon=PATH_ICON)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


myApp = App()

myApp.run()
