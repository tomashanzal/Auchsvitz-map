


from ursina import *
from ursina.shaders import unlit_shader  # DŮLEŽITÉ!
from ursina.prefabs.first_person_controller import FirstPersonController
app = Ursina()

# Hráč / kamera
player = FirstPersonController()
player.gravity = 0  # vypne gravitaci, takže nepadáš
player.cursor.visible = True
player.speed = 5  # rychlost pohybu

window.color = color.rgb(200, 200, 210)

def simple_house(position=(0,0,0), width=0, height=0, depth=0, wall_color=color.light_gray, roof_color=color.brown):
    x, y, z = position
    # Podlaha – volitelné
    floor = Entity(model='cube', scale=(width, 0.1, depth), position=(x, y, z), color=color.dark_gray)
    # Zdi
    wall_thickness = 0.2
    front = Entity(model='cube', scale=(width, height, wall_thickness), position=(x, y + height/2, z - depth/2), color=wall_color)
    back  = Entity(model='cube', scale=(width, height, wall_thickness), position=(x, y + height/2, z + depth/2), color=wall_color)
    left  = Entity(model='cube', scale=(wall_thickness, height, depth), position=(x - width/2, y + height/2, z), color=wall_color)
    right = Entity(model='cube', scale=(wall_thickness, height, depth), position=(x + width/2, y + height/2, z), color=wall_color)
    # Střecha – dva šikmé bloky
    roof_height = 0.7
    roof_left  = Entity(model='cube', scale=(width*0.8, wall_thickness, depth), position=(x+width/3, y + height*1.15 + roof_height/2, z),
                        rotation=(0,0,30), color=roof_color)
    roof_right = Entity(model='cube', scale=(width*0.8, wall_thickness, depth), position=(x-width/3, y + height*1.15 + roof_height/2, z),
                        rotation=(0,0,-30), color=roof_color)
    return [floor, front, back, left, right, roof_left, roof_right]

# Zeme
ground = Entity(
    model='plane',
    scale=(50, 1, 50),
    color=color.gray,
    texture='white_cube',
    texture_scale=(50, 50),
    collider='box'
)

houses = []
for i in range(2):
    houses += simple_house(position=(i*20, 0, 8), width=8, height=4, depth=16)
Entity(model='cube', color=color.red, shader=unlit_shader)

app.run()
