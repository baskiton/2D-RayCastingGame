from math import (inf, cos, sin, tan, atan2, hypot, pi, tau, degrees,
                  radians, log2)
from os import path
from tkinter import Tk, Canvas, NW, S, Label, messagebox

from PIL import Image, ImageTk


def exit_diag():
    answer = messagebox.askyesno(
        title="Выход", message="Вы действительно хотите выйти?"
    )
    if answer:
        close()
    else:
        root.event_generate(
            '<Key>', warp=True, x=(width >> 1), y=(height >> 1)
        )


def close():
    root.destroy()
    root.quit()


class KeyDetect:
    def __init__(self):
        self.pressed = {}
        self._set_bindings()

    def start(self):
        self.key()
        root.mainloop()

    def key(self):
        if (self.pressed['w'] or self.pressed['up']) and self.pressed['a']:
            player.move(2, -45)     # f-l
        elif (self.pressed['w'] or self.pressed['up']) and self.pressed['d']:
            player.move(2, 45)      # f-r
        elif (self.pressed['s'] or self.pressed['down']) and self.pressed['a']:
            player.move(-2, 45)     # b-l
        elif (self.pressed['s'] or self.pressed['down']) and self.pressed['d']:
            player.move(-2, -45)    # b-r
        elif self.pressed['w'] or self.pressed['up']:    # forward
            player.move(2, 0)
        elif self.pressed['s'] or self.pressed['down']:    # backward
            player.move(-2, 0)
        elif self.pressed['a']:    # turn left
            player.move(-2, 90)
        elif self.pressed['d']:    # turn right
            player.move(2, 90)
        if self.pressed['left']:    # rotate left
            player.rotate(-0.05)
        elif self.pressed['right']:    # rotate right
            player.rotate(0.05)
        # render(column_calculate())
        # player.show_marker()
        root.after(16, self.key)

    def _set_bindings(self):
        for char in ['w', 's', 'a', 'd', 'up', 'down', 'left', 'right']:
            root.bind('<KeyPress>', self._pressed)
            root.bind('<KeyRelease>', self._pressed)
            root.bind('<Motion>', self._mouse)
            self.pressed[char] = False

    def _pressed(self, event):
        # print(event.keysym)
        key_sym = event.keysym.lower()
        # print(key_sym)
        if str(event.type) == 'KeyRelease':
            modify = False
        elif event.keysym == 'Escape':
            exit_diag()
            return
        else:
            modify = True
            if key_sym == 'cyrillic_tse':
                key_sym = 'w'
            elif key_sym == 'cyrillic_ef':
                key_sym = 'a'
            elif key_sym == 'cyrillic_yeru':
                key_sym = 's'
            elif key_sym == 'cyrillic_ve':
                key_sym = 'd'
        if key_sym in self.pressed:
            self.pressed[key_sym] = modify

    @staticmethod
    def _mouse(event):
        diff = event.x - (width >> 1)
        m_sens = 0.0017 * diff
        player.rotate(m_sens)
        draw()
        root.event_generate(
            '<Key>', warp=True, x=(width >> 1), y=(height >> 1)
        )


class HUD:
    def __init__(self):
        self.b_g = ImageTk.PhotoImage(
            Image.open(textures['back']).resize((width, height))
        )
        self.mp = ImageTk.PhotoImage(
            Image.open(textures['map']).resize((img_w >> 2, img_h >> 2))
        )
        self.gn = ImageTk.PhotoImage(
            Image.open(textures['SPR_PISTOLREADY']).resize((320, 320))
        )

    def background(self):
        canvas.create_image(0, 0, anchor=NW, image=self.b_g, tag='background')

    def map(self):
        canvas.create_image(0, 0, anchor=NW, image=self.mp, tag='map')

    def gun(self):
        canvas.create_image(width >> 1, height, anchor=S,
                            image=self.gn, tag='gun')


class Player:
    def __init__(self):
        self.pos = [80, 80]
        self.heading = 0
        self.direction = [cos(self.heading), sin(self.heading)]
        self.marker = None
        self.marker_dir = None

    def rotate(self, angle):
        self.heading += angle
        self.direction = [cos(self.heading), sin(self.heading)]
        if self.heading > pi:
            self.heading -= tau
        elif self.heading < -pi:
            self.heading += tau

    def move(self, amt, k=None):
        if k is None:
            k = radians(0)
        z = radians(k)
        vel = [cos(self.heading + z) * amt,
               sin(self.heading + z) * amt]
        ff = list(map(lambda x, y: x + y, self.pos, vel))
        if not walls[int(ff[1]) >> bit_w][int(ff[0]) >> bit_w]:
            self.pos = ff

    def marker_create(self):
        self.marker = canvas.create_oval(
            self.pos[0]/4 - 2, self.pos[1]/4 - 2,
            self.pos[0]/4 + 2, self.pos[1]/4 + 2,
            fill='red', tag='marker'
        )
        self.marker_dir = canvas.create_line(
            self.pos[0]/4,
            self.pos[1]/4,
            self.pos[0]/4 + (self.direction[0] * 16),
            self.pos[1]/4 + (self.direction[1] * 16),
            fill='red', tag='marker'
        )

    def show_marker(self):
        canvas.coords(
            self.marker,
            self.pos[0]/4 - 2, self.pos[1]/4 - 2,
            self.pos[0]/4 + 2, self.pos[1]/4 + 2
        )
        canvas.coords(
            self.marker_dir,
            self.pos[0]/4,
            self.pos[1]/4,
            self.pos[0]/4 + (self.direction[0] * 16),
            self.pos[1]/4 + (self.direction[1] * 16)
        )


def sprites_calculate(col):
    k = 0
    for mob in mobs:
        sprite_dir = 0
        diff = sprite_dir - player.heading
        pos = [mob[0], mob[1]]

        diff_x = pos[0] - player.pos[0]
        diff_y = pos[1] - player.pos[1]
        dist = hypot(diff_x, diff_y)

        if diff > pi:
            sprite_dir -= tau
        elif diff < -pi:
            sprite_dir += tau

        sprite_dir = atan2(diff_y, diff_x)
        diff = sprite_dir - player.heading

        h_offset = degrees(diff) / fov * width + (width >> 1)
        if dist <= 8.868:
            sprite_size = 1000
        else:
            sprite_size = min(1000, int(8868 / dist))

        img_sprite = Image.open(mob[2])
        if dist in col:
            col[dist].append(
                ['sprite', h_offset, sprite_size, [img_sprite, 'sprite%s' % k]]
            )
        else:
            col[dist] = [
                ['sprite', h_offset, sprite_size, [img_sprite, 'sprite%s' % k]]
            ]
        k += 1
    return col


def sprite_marker():
    for mob in mobs:
        canvas.create_oval((mob[0] / 4) - 1, (mob[1] / 4) - 1,
                           (mob[0] / 4) + 1, (mob[1] / 4) + 1,
                           fill='red', outline='red', tag='marker')


def ray_distance(pos, angle):
    direction = [cos(angle), sin(angle)]
    a_y = (int(pos[1]) >> bit_w) << bit_w
    b_x = (int(pos[0]) >> bit_w) << bit_w
    x_a = y_a = x_b = y_b = 0
    dist_x = inf
    dist_y = inf
    alpha = tan(angle)

    if direction[1] >= 0:
        y_a = box_h
        a_y += box_h
    else:
        y_a = -box_h
        a_y -= 1

    if direction[0] >= 0:
        b_x += box_w
        x_b = box_w
    else:
        b_x -= 1
        x_b = -box_w

    if not alpha:
        x_a = inf
        a_x = -inf
    else:
        x_a = y_a / alpha
        a_x = pos[0] - (pos[1] - a_y) / alpha

    while True:
        if 0 < a_x < img_w and 0 < a_y < img_h:
            if walls[a_y >> bit_w][int(a_x) >> bit_w]:
                dist_y = hypot(a_x - pos[0], a_y - pos[1])
                break
            a_x += x_a
            a_y += y_a
            continue
        break

    y_b = x_b * alpha
    b_y = pos[1] - (pos[0] - b_x) * alpha

    while True:
        if 0 < b_x < img_w and 0 < b_y < img_h:
            if walls[int(b_y) >> bit_w][b_x >> bit_w]:
                dist_x = hypot(b_x - pos[0], b_y - pos[1])
                break
            b_x += x_b
            b_y += y_b
            continue
        break

    if min(dist_x, dist_y) == dist_x:
        dist = [dist_x, 'b']
    else:
        dist = [dist_y, 'a']
    return dist


def column_calculate():
    col = {}
    for i in range(-int(pixel_rate >> 1), int(pixel_rate >> 1)):
        dist_true = ray_distance(player.pos,
                                 (radians(i) / kef + player.heading))
        sq = dist_true[0] ** 2 / dov
        bright = (0 if sq > w_sq else (sq / w_sq) * (-255) + 255)
        if dist_true[1] == 'a':
            bright = bright * 0.8
        color = '#{0:02x}{0:02x}{0:02x}'.format(int(bright))

        '''
        ПЛОСКОСТЬ ПРОЕКЦИИ
        32 - размер кубов мира (box_w, box_h)
        277 - производная, равная X/tan(a), где:
            X - половина ширины плоскости проекции (разрешения картинки)
            a - половина угла fov
        8868 = 32 * 277 (увеличиваем скорость вычислений)
        Угол между последующими лучами = fov/2X градусов
        '''

        h = int(8868 / dist_true[0])    # column height
        if dist_true[0] in col:
            col[dist_true[0]].append(['wall', i, h, color])
        else:
            col[dist_true[0]] = [['wall', i, h, color]]

    return sprites_calculate(col)


def screen_init(c):
    for distance, value in sorted(c.items(), reverse=True):
        for spec in value:
            c_type, c_angle, c_height, c_color = spec
            if c_type == 'sprite':
                img_sprite = c_color[0].resize((c_height, c_height))
                pic = ImageTk.PhotoImage(img_sprite)
                canvas.create_image(
                    c_angle, rect_mode[1], image=pic,
                    tags=('sprite', c_color[1])
                )
                label = Label(canvas, image=pic)
                label.image = pic
                label.name = c_color[1]
                label.pack()
                labels.append(label)
                label.destroy()
            elif c_type == 'wall':
                x = rect_mode[0] + 1 + (c_angle + (pixel_rate >> 1)) * column_w
                canvas.create_line(
                    x, rect_mode[1] - (c_height >> 1),
                    x, rect_mode[1] + (c_height >> 1),
                    width=column_w, fill=c_color, tags='wall' + str(x)
                )


def render(c):
    for distance, value in sorted(c.items(), reverse=True):
        for spec in value:
            c_type, c_angle, c_height, c_color = spec
            if c_type == 'sprite':
                if (-c_height - 5) <= c_angle <= (width + c_height + 5):
                    img_sprite = c_color[0].resize((c_height, c_height))
                    pic = ImageTk.PhotoImage(img_sprite)
                    canvas.itemconfig(c_color[1], image=pic)
                    canvas.coords(c_color[1], c_angle, rect_mode[1])
                    canvas.tag_raise(c_color[1])
                    label = Label(canvas, image=pic)
                    label.image = pic
                    label.name = c_color[1]
                    label.pack()
                    labels.append(label)
                    label.destroy()
            elif c_type == 'wall':
                x = rect_mode[0] + 1 + (c_angle + (pixel_rate >> 1)) * column_w
                tag = 'wall' + str(x)
                canvas.itemconfig(tag, width=column_w, fill=c_color)
                canvas.coords(
                    tag,
                    x, rect_mode[1] - (c_height >> 1),
                    x, rect_mode[1] + (c_height >> 1)
                )
                canvas.tag_raise(tag)


def draw():
    labels.clear()
    render(column_calculate())
    canvas.tag_raise('map')
    canvas.tag_raise('gun')
    player.show_marker()
    canvas.tag_raise('marker')


if __name__ == "__main__":
    root = Tk()
    root.title("2D Ray Casting")
    root.protocol('WM_DELETE_WINDOW', exit_diag)

    width = 640
    height = 400

    textures = {
        'map': path.join('res', 'map.gif'),
        'SPR_PISTOLREADY': path.join('res', 'SPR_PISTOLREADY.gif'),
        'back': path.join('res', 'back.gif'),
        'soldier': path.join('res', 'soldier.gif'),
        'MAP': path.join('res', 'map.bmp'),
        'SPR_STAT_14': path.join('res', 'SPR_STAT_14.gif'),
        'SPR_STAT_22_(Spear)': path.join('res', 'SPR_STAT_22_(Spear).gif'),
        'SPR_STAT_44_(Spear)': path.join('res', 'SPR_STAT_44_(Spear).gif'),
        'SPR_STAT_16': path.join('res', 'SPR_STAT_16.gif'),
        'SPR_STAT_8': path.join('res', 'SPR_STAT_8.gif')
    }

    walls = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    mobs = [
        [80, 300, textures['soldier']],
        [209, 365, textures['soldier']],
        [48, 433, textures['soldier']],
        [450, 264, textures['soldier']],
        [240, 48, textures['SPR_STAT_14']],
        [304, 48, textures['SPR_STAT_14']],
        [368, 48, textures['SPR_STAT_14']],
        [176, 240, textures['SPR_STAT_22_(Spear)']],
        [240, 240, textures['SPR_STAT_22_(Spear)']],
        [208, 240, textures['SPR_STAT_44_(Spear)']],
        [472, 464, textures['SPR_STAT_16']],
        [472, 472, textures['SPR_STAT_8']]
    ]

    map_w = 16
    map_h = 16
    img_w = 512
    img_h = 512
    box_w = int(img_w / map_w)  # 32
    box_h = int(img_h / map_h)  # 32
    bit_w = int(log2(box_w))
    bit_h = int(log2(box_h))
    w_sq = img_w ** 2

    dov = 1     # distance of view
    fov = 60    # field of view
    pixel_rate = 160
    kef = pixel_rate / fov
    rect_mode = [0, height >> 1]
    column_w = width / pixel_rate

    canvas = Canvas(root, height=height, width=width,
                    bg='black', cursor="none")
    canvas.focus_set()
    canvas.pack()

    player = Player()
    hud = HUD()
    labels = []

    hud.background()
    columns = column_calculate()
    screen_init(columns)
    hud.map()
    sprite_marker()
    player.marker_create()
    hud.gun()

    KeyDetect().start()
