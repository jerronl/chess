import pygame,pygame_gui,os,json

def find_windows_font(name_contains):
    font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    for fname in os.listdir(font_dir):
        if name_contains.lower() in fname.lower():
            return os.path.join(font_dir, fname)
    return None

def launch_control_panel():
    pygame.init()
    pygame.display.set_caption("象棋对局设置")
    window_size = (400, 300)
    window_surface = pygame.display.set_mode(window_size)
    with open("./assets/themes.json", encoding="utf-8") as f:
        theme_dict = json.load(f)

    # 动态添加字体路径和默认字体设置
    font_path = find_windows_font(theme_dict["defaults"]["font"]['name'])
    if font_path is None:
        raise FileNotFoundError(f"未找到 {theme_dict["defaults"]["font"]['name']}")

    theme_dict["defaults"]["font"]['file_path'] = font_path
    theme_dict["defaults"]["font"]['regular_path'] = font_path
    theme_dict["font"]['regular_path'] = font_path
    manager = pygame_gui.UIManager((600, 400), theme_path=theme_dict)
    # manager.preload_fonts([theme_dict["defaults"]["font"]])
    cfont = pygame.font.Font(font_path, theme_dict["defaults"]["font"]['size'])
    # 红方控制
    red_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((30, 20), (100, 30)),
        text="红方控制：",
        manager=manager
    )
    red_human_btn = pygame_gui.elements.UIButton(
        pygame.Rect((140, 20), (100, 30)),
        text="玩家",
        manager=manager,
        object_id=pygame_gui.core.ObjectID("#red_human", "@red_button")
    )
    
    red_ai_btn = pygame_gui.elements.UIButton(
        pygame.Rect((250, 20), (100, 30)),
        text="AI",
        manager=manager,
        object_id=pygame_gui.core.ObjectID("#red_ai", "@red_button")
    )

    black_human_btn = pygame_gui.elements.UIButton(
        pygame.Rect((140, 70), (100, 30)),
        text="玩家",
        manager=manager,
        object_id=pygame_gui.core.ObjectID("#black_human", "@black_button")
    )
    black_ai_btn = pygame_gui.elements.UIButton(
        pygame.Rect((250, 70), (100, 30)),
        text="AI",
        manager=manager,
        object_id=pygame_gui.core.ObjectID("#black_ai", "@black_button")
    )

    # 黑方控制
    black_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((30, 70), (100, 30)),
        text="黑方控制：",
        manager=manager
    )

    # AI 思考时间滑块
    slider_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((30, 120), (150, 30)),
        text="AI 思考时间（ms）：",
        manager=manager
    )
    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((30, 150), (320, 25)),
        start_value=1000,
        value_range=(100, 10000),
        manager=manager
    )
    slider_value = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((30, 180), (320, 30)),
        text="当前：1000 ms",
        manager=manager
    )

    # 开始按钮
    start_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((150, 230), (100, 40)),
        text="开始游戏",
        manager=manager
    )
    # for ctl in (red_ai_btn,red_human_btn,red_label,black_ai_btn,black_human_btn,black_label,slider_label,slider_value,start_btn):
    #     ctl.font = cfont
        
    clock = pygame.time.Clock()
    is_running = True
    red_ai = False
    black_ai = False
    think_time = 1000

    def update_buttons():
        red_human_btn.select() if not red_ai else red_human_btn.unselect()
        red_ai_btn.select() if red_ai else red_ai_btn.unselect()
        black_human_btn.select() if not black_ai else black_human_btn.unselect()
        black_ai_btn.select() if black_ai else black_ai_btn.unselect()

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == red_human_btn:
                        red_ai = False
                    elif event.ui_element == red_ai_btn:
                        red_ai = True
                    elif event.ui_element == black_human_btn:
                        black_ai = False
                    elif event.ui_element == black_ai_btn:
                        black_ai = True
                    elif event.ui_element == start_btn:
                        is_running = False  # close panel

                    update_buttons()

                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == slider:
                        think_time = int(slider.get_current_value())
                        slider_value.set_text(f"当前：{think_time} ms")

            manager.process_events(event)

        manager.update(time_delta)
        window_surface.fill((255, 255, 255))
        manager.draw_ui(window_surface)
        pygame.display.update()

    # pygame.quit()
    return {
        "red_ai": red_ai,
        "black_ai": black_ai,
        "think_time": think_time
    }
