from tkinter import Tk, Canvas, NW, S, Label, PhotoImage, messagebox
from math import inf, cos, sin, atan2, tan, hypot, pi, tau, radians, degrees, log2
from PIL import Image, ImageTk

root = Tk()
root.title("2D Ray Casting")
frame_count = 0


class HUD:
    def __init__(self):
        # self.mp = ImageTk.PhotoImage(maps.resize((img_w, img_h)))
        # canvas.create_image(0, 0, anchor=NW, image=mp)
        pass

    def bck_g(self):
        global b_g
        b_g = ImageTk.PhotoImage(bg_i.resize((width, height)))
        label = Label(canvas, image=b_g)
        label.image = b_g
        label.pack()
        label.destroy()

    def map(self):
        global mp
        txt = Image.open(textures[0])
        mp = ImageTk.PhotoImage(txt.resize((img_w >> 2, img_h >> 2)))
        label = Label(canvas, image=mp)
        label.image = mp
        label.pack()
        label.destroy()

    def gun(self):
        global hand
        txt = Image.open(textures[1])
        hand = ImageTk.PhotoImage(txt.resize((320, 320)))
        label = Label(canvas, image=hand)
        label.image = hand
        label.pack()
        label.destroy()


class Walls:
    def __init__(self, ax, ay, bx, by):
        self.a = [ax, ay]
        self.b = [bx, by]
        pass

    def show(self):
        canvas.create_line(self.a[0], self.a[1], self.b[0], self.b[1], fill="blue", width=1)


class Ray:
    def __init__(self, pos, angle):
        self.pos = pos
        self.dir = list((cos(angle), sin(angle)))
        self.heading = angle
        # self.pt = [0, 0]
        pass

    # def set_angle(self, angle):
    #     self.dir = list((cos(angle), sin(angle)))

    def cast(self):
        global stein
        a_y = (int(self.pos[1]) >> bit_w) << bit_w
        b_x = (int(self.pos[0]) >> bit_w) << bit_w
        x_a, y_a = 0, 0
        x_b, y_b = 0, 0
        dist_x = inf
        dist_y = inf

        a = tan(self.heading)

        if self.dir[1] >= 0:
            y_a = box_h
            a_y += box_h
        elif self.dir[1] < 0:
            y_a = -box_h
            a_y -= 1

        if self.dir[0] >= 0:
            b_x += box_w
            x_b = box_w
        elif self.dir[0] < 0:
            b_x -= 1
            x_b = -box_w

        if not a:
            x_a = inf
            a_x = -inf
        else:
            x_a = y_a / a
            a_x = self.pos[0] - (self.pos[1] - a_y) / a

        while True:
            if 0 < a_x < img_w and 0 < a_y < img_h:
                if walls()[a_y >> bit_w][int(a_x) >> bit_w]:
                    dist_y = hypot(a_x - self.pos[0], a_y - self.pos[1])
                    break
                else:
                    a_x += x_a
                    a_y += y_a
                    continue
            break

        y_b = x_b * a
        b_y = self.pos[1] - (self.pos[0] - b_x) * a

        while True:
            if 0 < b_x < img_w and 0 < b_y < img_h:
                if walls()[int(b_y) >> bit_w][b_x >> bit_w]:
                    dist_x = hypot(b_x - self.pos[0], b_y - self.pos[1])
                    break
                else:
                    b_x += x_b
                    b_y += y_b
                    continue
            break

        if min(dist_x, dist_y) == dist_x:
            # self.pt = [b_x, b_y]
            dist = [dist_x, 'b']
            stein = 'b'
        else:
            # self.pt = [a_x, a_y]
            dist = [dist_y, 'a']
            stein = 'a'
        # canvas.create_line(self.pos[0] / 4, self.pos[1] / 4, self.pt[0] / 4, self.pt[1] / 4, fill='blue')
        return dist


class Particle:
    def __init__(self):
        self.pos = [80, 80]
        self.heading = 0
        self.scene = []
        self.dir = [1, 0]
        self.pt = [0, 0]
        pass

    def rotate(self, angle):
        self.heading += angle
        self.dir = list((cos(self.heading), sin(self.heading)))

        if self.heading > pi:
            self.heading -= tau
        elif self.heading < -pi:
            self.heading += tau
        return self.heading

    def move(self, amt):
        # self.pos = self.pos
        vel = list((cos(self.heading) * amt, sin(self.heading) * amt))
        ff = list(map(lambda x, y: x + y, self.pos, vel))
        # self.pos = list(map(lambda x, y: x + y, self.pos, vel))
        if walls()[int(ff[1]) >> bit_w][int(ff[0]) >> bit_w]:
            self.pos = self.pos
            # if stein == 'a':
            #     self.pos[0] = ff[0]
            #     self.pos[1] = self.pos[1]
            # elif stein == 'b':
            #     self.pos[0] = self.pos[0]
            #     self.pos[1] = ff[1]
        else:
            self.pos = ff
        return self.pos

    def move_side(self, amt):
        vel = list((cos(self.heading + radians(90)) * amt, sin(self.heading + radians(90)) * amt))
        ff = list(map(lambda x, y: x + y, self.pos, vel))
        # self.pos = list(map(lambda x, y: x + y, self.pos, vel))
        if walls()[int(ff[1]) >> bit_w][int(ff[0]) >> bit_w]:
            self.pos = self.pos
            # if stein == 'a':
            #     self.pos[0] = ff[0]
            #     self.pos[1] = self.pos[1]
            # elif stein == 'b':
            #     self.pos[0] = self.pos[0]
            #     self.pos[1] = ff[1]
        else:
            self.pos = ff
        return self.pos

    def update(self):
        global column
        global column_key
        column = {}
        column_key = []
        for i in range(-int(pix_rate >> 1), int(pix_rate >> 1)):
            s1 = i / kef + self.heading
            dist_true = Ray(self.pos, (radians(i) / kef + self.heading)).cast()
            # dist_corr = dist_true[0] * cos(radians(s1))
            dist_corr = dist_true[0]
            sq = dist_true[0] ** 2 / dov
            b = (0 if sq > w_sq else (sq / w_sq) * (- 255) + 255)
            if dist_true[1] == 'a':
                b = b * 0.8

            rec_c = '#' + ('%02x' % int(b)) * 3
            '''
            ПЛОСКОСТЬ ПРОЕКЦИИ
            32 - размер кубов мира
            277 - производная, равная X/tan(a), где:
                                            X - половина ширины плоскости проекции (разрешения картинки)
                                            a - половина угла fov
            8868 = 32 * 277 (увеличиваем скорость вычислений)
            Угол между последующими лучами = fov/2X градусов
            '''
            h = int(8868 / dist_corr)

            if dist_true[0] in column:
                column[dist_true[0]].append(['column', i, h, rec_c])
            else:
                column[dist_true[0]] = [['column', i, h, rec_c]]
                column_key.append(dist_true[0])

    def show(self):
        canvas.create_oval(self.pos[0]/4 - 2, self.pos[1]/4 - 2, self.pos[0]/4 + 2, self.pos[1]/4 + 2, fill='red')
        canvas.create_line(self.pos[0]/4,
                           self.pos[1]/4,
                           self.pos[0]/4 + (self.dir[0] * 16),
                           self.pos[1]/4 + (self.dir[1] * 16),
                           fill='red')


class Sprite:
    def __init__(self):
        self.pos = []
        self.dist = 0
        self.k = 0
        self.sprite_dir = 0

    def draw(self):
        global sprites
        sprites = {}
        for mob in mobs():
            self.pos = [mob[0], mob[1]]

            img_sprite = Image.open(mob[2])

            diff_x = self.pos[0] - player_pos[0]
            diff_y = self.pos[1] - player_pos[1]
            self.dist = hypot(diff_x, diff_y)

            diff = self.sprite_dir - player_dir
            if diff > pi:
                self.sprite_dir -= tau
            elif diff < -pi:
                self.sprite_dir += tau

            self.sprite_dir = atan2(diff_y, diff_x)
            diff = self.sprite_dir - player_dir

            h_offset = degrees(diff) / fov * width + (width >> 1)
            if self.dist <= 8.868:
                sprite_size = 1000
            else:
                sprite_size = min(1000, int(8868 / self.dist))

            pic = ImageTk.PhotoImage(img_sprite.resize((sprite_size, sprite_size)))
            label = Label(canvas, image=pic)
            label.image = pic
            label.pack()

            if (-sprite_size) <= h_offset <= (width + sprite_size):
                if self.dist in column:
                    column[self.dist].append(['sprite', h_offset, sprite_size, pic])
                else:
                    column[self.dist] = [['sprite', h_offset, sprite_size, pic]]
                    column_key.append(self.dist)
            label.destroy()

    def show(self):
        for mob in mobs():
            canvas.create_oval((mob[0] / 4) - 1, (mob[1] / 4) - 1,
                               (mob[0] / 4) + 1, (mob[1] / 4) + 1,
                               fill='red', outline='red')


class Render:
    def __init__(self, a):
        self.dict = a

    def render(self):
        column_key.sort(reverse=True)
        for i in column_key:
            for j in column[i]:
                if j[0] == 'sprite':
                    canvas.create_image(j[1], rect_mode[1], image=j[3])
                elif j[0] == 'column':
                    canvas.create_line(rect_mode[0] + ((j[1] + (pix_rate >> 1)) * w), rect_mode[1] - (j[2] >> 1),
                                       rect_mode[0] + ((j[1] + (pix_rate >> 1)) * w), rect_mode[1] + (j[2] >> 1),
                                       width=w, fill=j[3])


def walls():
    # img = Image.open('res/map.bmp')
    # pixels = img.load()
    wall = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1],
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
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    return wall


def mobs():
    mob = [(80, 300, textures[3]),
           (209, 365, textures[3]),
           (48, 433, textures[3]),
           (450, 264, textures[3]),
           (240, 48, textures[5]),
           (304, 48, textures[5]),
           (368, 48, textures[5]),
           (176, 240, textures[6]),
           (240, 240, textures[6]),
           (208, 240, textures[7]),
           (472, 464, textures[8]),
           (472, 472, textures[9])]
    return mob


def setup():
    global img_w
    global img_h
    global width
    global height
    global fov
    global pix_rate
    global kef
    global particle
    global canvas
    global sprite
    global map_w
    global map_h
    global box_h
    global box_w
    global bit_w
    global bit_h
    global bg_i
    global player_pos
    global player_dir
    global textures

    global rect_mode
    global w
    global dov
    global w_sq
    global hud

    # global wall

    global stein
    stein = ''

    textures = ['res/map.gif', 'res/SPR_PISTOLREADY.gif', 'res/back.gif', 'res/soldier.gif',
                'res/map.bmp', 'res/SPR_STAT_14.gif', 'res/SPR_STAT_22_(Spear).gif', 'res/SPR_STAT_44_(Spear).gif',
                'res/SPR_STAT_16.gif', 'res/SPR_STAT_8.gif']

    # img = Image.open(textures[4])
    # wall = img.load()

    map_w = 16
    map_h = 16
    img_w = 512
    img_h = 512
    box_w = 32  # img_w / map_w
    box_h = 32  # img_h / map_h
    bit_w = int(log2(box_w))
    bit_h = int(log2(box_h))
    width = 640
    height = 400

    fov = 60
    pix_rate = 160
    kef = pix_rate / fov

    particle = Particle()
    player_pos = particle.move(0)
    player_dir = particle.rotate(0)
    sprite = Sprite()
    hud = HUD()

    canvas = Canvas(root, height=height, width=width, bg='black', cursor="None")
    canvas.pack()

    bg_i = Image.open(textures[2])

    rect_mode = [0, height >> 1]
    w = width / pix_rate
    dov = 1
    w_sq = img_w ** 2


def draw():
    canvas.delete('all')

    hud.bck_g()
    canvas.create_image(0, 0, anchor=NW, image=b_g)

    particle.update()

    sprite.draw()

    Render(column).render()

    hud.map()
    canvas.create_image(0, 0, anchor=NW, image=mp)

    particle.show()
    sprite.show()

    hud.gun()
    canvas.create_image(width >> 1, height, anchor=S, image=hand)


class KeyDetect:
    def __init__(self):
        self.pressed = {}
        self._set_bindings()

    def start(self):
        self.key()
        root.mainloop()

    def key(self):
        global player_pos
        global player_dir

        if self.pressed[87] or self.pressed[38]:
            player_pos = particle.move(2)
            draw()
        if self.pressed[83] or self.pressed[40]:
            player_pos = particle.move(-2)
            draw()
        if self.pressed[65]:
            player_pos = particle.move_side(-2)
            draw()
        if self.pressed[68]:
            player_pos = particle.move_side(2)
            draw()
        if self.pressed[37]:
            player_dir = particle.rotate(-0.05)
            draw()
        if self.pressed[39]:
            player_dir = particle.rotate(0.05)
            draw()
        root.after(16, self.key)

    def _set_bindings(self):
        for char in [87, 83, 38, 40, 65, 68, 37, 39]:
            root.bind("<KeyPress>", self._pressed)
            root.bind("<KeyRelease>", self._released)
            root.bind('<Motion>', self._mouse)
            self.pressed[char] = False

    def _pressed(self, event):
        # print(event.keycode)
        if event.keycode == 27:
            exit_diag()
        else:
            self.pressed[event.keycode] = True

    def _released(self, event):
        self.pressed[event.keycode] = False

    def _mouse(self, event):
        global player_dir
        diff = event.x - (width >> 1)
        m_sens = 0.0017 * diff
        if event.x < (width >> 1):
            player_dir = particle.rotate(m_sens)
            draw()
        elif event.x > (width >> 1):
            player_dir = particle.rotate(m_sens)
            draw()
        root.event_generate('<Key>', warp=True, x=(width >> 1), y=(height >> 1))


def exit_diag():
    answer = messagebox.askyesno(title="", message="Вы действительно хотите выйти?")
    if answer:
        close()
    else:
        root.event_generate('<Key>', warp=True, x=(width >> 1), y=(height >> 1))


def close():
    root.destroy()
    root.quit()


root.protocol('WM_DELETE_WINDOW', exit_diag)

if __name__ == "__main__":
    setup()
    draw()
    k = KeyDetect()
    k.start()
