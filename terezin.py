from ursina import *
from ursina.shaders import unlit_shader
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Hráč / kamera
player = FirstPersonController()
player.gravity = 0
player.cursor.visible = True
player.speed = 40
camera.clip_plane_far = 500 # Zvýšil jsem dohled, aby bylo vidět více, pokud výkon dovolí.

# Zeme
ground = Entity(
    model='plane',
    scale=(1000, 1, 1000),
    color=color.gray,
    texture='white_cube',
    texture_scale=(1000, 1000),
    collider='box',
    shader=unlit_shader # Ujistil jsem se, že i zem používá unlit_shader
)

window.color = color.rgb(200, 200, 210)

def create_road_segment(position=(0, 0, 0), length=50, width=5, rotace=0):
    # Tato funkce jen vrací jedinou entitu pro segment silnice.
    # Sloučení silnic je prováděno až v hlavní smyčce.
    x, y, z = position
    road = Entity(
        model='cube',
        scale=(width, 0.1, length),
        position=(x, y, z),
        color=color.hex('#2B2B2B'),  # tmavý asfalt
        texture='white_cube',
        texture_scale=(width, length),
        shader=unlit_shader,
        collider='box', # silnice by měla mít kolider
        rotation_y=rotace
    )
    return road

def create_simple_house(position=(0,0,0), width=0, height=0, depth=0, wall_color=color.hex("#424242"), roof_color=color.hex("#321E1E"), rotation=(0,0,0)):
    # x, y, z = position # Již nepotřebujeme rozkládat pozici zde, nastavíme ji na combined_house
    house_parts_to_combine = [] # Seznam pro části, které se budou kombinovat

    # Podlaha – volitelné
    # Důležité: Nastavujeme pozice částí RELATIVNĚ k (0,0,0), což bude střed budoucí combined_house entity.
    house_parts_to_combine.append(Entity(model='cube', scale=(width, 0.1, depth), position=(0, 0, 0), color=color.dark_gray))

    # Zdi
    wall_thickness = 0.2
    house_parts_to_combine.append(Entity(model='cube', scale=(width, height, wall_thickness), position=(0, height/2, -depth/2), color=wall_color))
    house_parts_to_combine.append(Entity(model='cube', scale=(width, height, wall_thickness), position=(0, height/2, depth/2), color=wall_color))
    house_parts_to_combine.append(Entity(model='cube', scale=(wall_thickness, height, depth), position=(-width/2, height/2, 0), color=wall_color))
    house_parts_to_combine.append(Entity(model='cube', scale=(wall_thickness, height, depth), position=(width/2, height/2, 0), color=wall_color))

    # Střecha – dva šikmé bloky
    roof_height = 0.7
    house_parts_to_combine.append(Entity(model='cube', scale=(width*0.8, wall_thickness, depth), position=(width/3, height*1.15 + roof_height/2, 0), rotation=(0,0,30), color=roof_color))
    house_parts_to_combine.append(Entity(model='cube', scale=(width*0.8, wall_thickness, depth), position=(-width/3, height*1.15 + roof_height/2, 0), rotation=(0,0,-30), color=roof_color))
    
    # Sloučí všechny části domu do jedné entity
    # combined_house dostane pozici a rotaci. Collider bude na celou entitu.
    combined_house = Entity(
        model=None, 
        collider='box', 
        shader=unlit_shader, 
        position=position, # Nastavujeme globální pozici zde
        rotation=rotation   # A rotaci zde
    ) 
    
    for part in house_parts_to_combine:
        part.parent = combined_house
        # Pozice částí jsou již relativní k (0,0,0), takže je nemusíme odečítat ani měnit
        part.shader = unlit_shader
    
    combined_house.combine() 
    return combined_house


def create_fence_segment(start=(0, 0, 0), length=10, spacing=2, axis='x'):
    x, y, z = start
    height = 5
    post_width = 0.1
    bar_thickness = 0.1
    bar_count = 12
    
    fence_parts = [] # Místo 'parts' nyní 'fence_parts'
    int_length = int(length / spacing) # Počet segmentů plotu

    for i in range(int_length + 1):
        if axis == 'x':
            px = x + i * spacing
            post = Entity(model='cube', scale=(post_width, height, post_width),
                          position=(px, y + height / 2, z),
                          color=color.hex("#424242"), texture='white_cube',
                          shader=unlit_shader, collider='box')
            fence_parts.append(post)

            if i < int_length:
                for j in range(bar_count):
                    bar_y = y + height - 0.3 - j * 0.4
                    bar = Entity(model='cube',
                                 scale=(spacing - post_width, bar_thickness, bar_thickness),
                                 position=(px + spacing / 2, bar_y, z),
                                 color=color.hex("#424242"), texture='white_cube',
                                 shader=unlit_shader) # Kolider není nutný pro každou tyčku
                    fence_parts.append(bar)
        elif axis == 'y':
            pz = z + i * spacing
            post = Entity(model='cube', scale=(post_width, height, post_width),
                          position=(x, y + height / 2, pz),
                          color=color.hex("#424242"), texture='white_cube',
                          shader=unlit_shader, collider='box')
            fence_parts.append(post)

            if i < int_length:
                for j in range(bar_count):
                    bar_y = y + height - 0.3 - j * 0.4
                    bar = Entity(model='cube',
                                 scale=(bar_thickness, bar_thickness, spacing - post_width),
                                 position=(x, bar_y, pz + spacing / 2),
                                 color=color.hex("#424242"), texture='white_cube',
                                 shader=unlit_shader) # Kolider není nutný pro každou tyčku
                    fence_parts.append(bar)
    
    # Sloučení všech částí plotu do jedné entity
    combined_fence = Entity(model=None, shader=unlit_shader, color=color.white)
    # Zde je důležité, aby se všechny díly staly dětmi combined_fence před voláním combine()
    for part in fence_parts:
        part.parent = combined_fence
        part.position -= combined_fence.position # Nastavíme pozice relativně k rodiči
        part.shader = unlit_shader # Zajistíme, že i jednotlivé části před sloučením mají unlit_shader
    
    combined_fence.combine() # Sloučí všechny modely do jednoho
    
    # Zde můžete nastavit jeden velký kolider pro celý plot, pokud je potřeba pro interakci s hráčem
    # combined_fence.collider = 'box' 
    # NEBO
    # combined_fence.collider = MeshCollider(combined_fence, mesh=combined_fence.model) # složitější, ale přesnější
    
    return combined_fence


def create_tower(position=(0, 0, 0)):
    x, y, z = position
    tower_height = 6
    leg_distance = 1.5
    leg_thickness = 0.2
    cabin_size = 2.5
    roof_thickness = 0.1
    ladder_step_count = 10
    ladder_spacing = tower_height / ladder_step_count

    wood_color = color.hex('#4B3A2F')
    cabin_color = color.hex('#2E2E2E')
    roof_color = color.hex('#1B1B1B')
    ladder_color = color.hex('#6F6F6F')
    
    tower_parts = []

    # 4 nohy věže
    for dx in [-leg_distance/2, leg_distance/2]:
        for dz in [-leg_distance/2, leg_distance/2]:
            leg = Entity(model='cube', scale=(leg_thickness, tower_height, leg_thickness),
                         position=(x + dx, y + tower_height / 2, z + dz),
                         color=wood_color, texture='white_cube', shader=unlit_shader)
            tower_parts.append(leg)

    # Podlaha kabiny
    floor = Entity(model='cube', scale=(cabin_size, 0.1, cabin_size),
                   position=(x, y + tower_height + 0.05, z),
                   color=wood_color, texture='white_cube', shader=unlit_shader)
    tower_parts.append(floor)

    # Stěny kabiny (čtyři)
    wall_thickness = 0.1
    wall_height = 2
    for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        wall = Entity(model='cube', scale=(cabin_size if dx == 0 else wall_thickness,wall_height,cabin_size if dz == 0 else wall_thickness),
                      position=(x + dx * (cabin_size/2 - wall_thickness/2),y + tower_height + wall_height / 2,z + dz * (cabin_size/2 - wall_thickness/2)),
                      color=cabin_color, texture='white_cube', shader=unlit_shader)
        tower_parts.append(wall)

    # Střecha
    roof = Entity(model='cube', scale=(cabin_size + 0.3, roof_thickness, cabin_size + 0.3),
                  position=(x, y + tower_height + wall_height + roof_thickness / 2, z),
                  color=roof_color, texture='white_cube', shader=unlit_shader)
    tower_parts.append(roof)

    # Žebřík
    for i in range(ladder_step_count):
        step_y = y + i * ladder_spacing + 0.2
        step = Entity(model='cube', scale=(cabin_size - 0.3, 0.1, 0.05),
                      position=(x, step_y, z - leg_distance/2 - 0.1),
                      color=ladder_color, texture='white_cube', shader=unlit_shader)
        tower_parts.append(step)
    
    # Sloučení všech částí věže do jedné entity
    combined_tower = Entity(model=None, collider='box', shader=unlit_shader, color=color.white) # Collider pro celou věž
    for part in tower_parts:
        part.parent = combined_tower
        part.position -= combined_tower.position
        part.shader = unlit_shader
    
    combined_tower.combine()
    return combined_tower


def create_rails_segment(start=(0, 0, 0), length=20, spacing=1.0):
    x, y, z = start
    sleeper_width = 1.8
    sleeper_depth = 0.2
    sleeper_thickness = 0.1
    rail_height = 0.15
    rail_width = 0.07
    rail_spacing = 1.0
    sleeper_color = color.hex('#4E3629')
    rail_color = color.hex('#A0A0A0')
    
    rail_parts = []
    
    for i in range(length):
        z_pos = z + i * spacing
        # Pražec
        sleeper = Entity(model='cube',
                         scale=(sleeper_width, sleeper_thickness, sleeper_depth),
                         position=(x, y + sleeper_thickness / 2, z_pos),
                         color=sleeper_color, shader=unlit_shader, texture='white_cube')
        rail_parts.append(sleeper)
        
        # Levá kolejnice
        left_rail = Entity(model='cube',
                           scale=(rail_width, rail_height, spacing + 0.01),
                           position=(x - rail_spacing / 2, y + sleeper_thickness + rail_height / 2, z_pos + spacing / 2 - spacing / 2),
                           color=rail_color, shader=unlit_shader, texture='white_cube')
        rail_parts.append(left_rail)
        
        # Pravá kolejnice
        right_rail = Entity(model='cube',
                            scale=(rail_width, rail_height, spacing + 0.01),
                            position=(x + rail_spacing / 2, y + sleeper_thickness + rail_height / 2, z_pos + spacing / 2 - spacing / 2),
                            color=rail_color, shader=unlit_shader, texture='white_cube')
        rail_parts.append(right_rail)
    
    # Sloučení všech částí kolejí do jedné entity
    combined_rails = Entity(model=None, shader=unlit_shader, color=color.white)
    for part in rail_parts:
        part.parent = combined_rails
        part.position -= combined_rails.position
        part.shader = unlit_shader
    
    combined_rails.combine()
    return combined_rails


def create_gate(position=(0, 0, 0)):
    x, y, z = position
    gate_parts = []

    # Rozměry
    base_width = 30
    base_depth = 6
    base_height = 6
    tower_height = 8
    tower_width = 7
    gate_height = 5
    gate_width_each = 2.5
    gate_opening_width = gate_width_each * 2 + 0.2

    brick_color = color.hex('#4A2E1F')
    roof_color = color.hex('#2A2A2A')

    # Levá část hlavní budovy (před dírou)
    left_base = Entity(
        model='cube',
        scale=((base_width - gate_opening_width) / 2, base_height, base_depth),
        position=(x - (gate_opening_width + (base_width - gate_opening_width) / 2) / 2,
                  y + base_height / 2,
                  z),
        color=brick_color,
        shader=unlit_shader,
        collider='box' # Kolider pro základnu
    )
    gate_parts.append(left_base)

    # Pravá část hlavní budovy (za dírou)
    right_base = Entity(
        model='cube',
        scale=((base_width - gate_opening_width) / 2, base_height, base_depth),
        position=(x + (gate_opening_width + (base_width - gate_opening_width) / 2) / 2,
                  y + base_height / 2,
                  z),
        color=brick_color,
        shader=unlit_shader,
        collider='box' # Kolider pro základnu
    )
    gate_parts.append(right_base)

    # Věž nad průjezdem
    tower_main = Entity(
        model='cube',
        scale=(tower_width, tower_height, base_depth),
        position=(x, y + base_height + tower_height / 2 -1, z),
        color=brick_color,
        shader=unlit_shader,
        collider='box' # Kolider pro věž
    )
    gate_parts.append(tower_main)

    # Šikmá střecha věže (2 části)
    roof_y = y + base_height + tower_height -0.5
    for side in (-1, 1):
        roof = Entity(
            model='cube',
            scale=(tower_width -1.4, 0.2, base_depth),
            position=(x + side * 2.4, roof_y, z),
            rotation=(0, 0, side * 25),
            color=roof_color,
            shader=unlit_shader
        )
        gate_parts.append(roof)

    # Brána – dvoukřídlá kovová mříž
    gate_thickness = 0.15
    gate_segments = 7

    for side in (-1, 1):
        for i in range(gate_segments):
            bar = Entity(
                model='cube',
                scale=(gate_thickness, gate_height, gate_thickness),
                position=(
                    x + side * (gate_width_each / 2) + (i - gate_segments // 2) * 0.4,
                    y + gate_height / 2,
                    z
                ),
                color=color.hex('#333333'),
                shader=unlit_shader
            )
            gate_parts.append(bar)
    
    # Sloučení všech částí brány do jedné entity
    combined_gate = Entity(model=None, shader=unlit_shader, color=color.white)
    # Pro bránu nastavíme collider na Combined mesh až po combine
    for part in gate_parts:
        part.parent = combined_gate
        part.position -= combined_gate.position
        part.shader = unlit_shader
    
    combined_gate.combine()
    # Můžete nastavit MeshCollider pro přesnější kolize s bránou, pokud potřebujete.
    # Ale 'box' na combined_gate může být dostatečný a méně náročný.
    # combined_gate.collider = MeshCollider(combined_gate, mesh=combined_gate.model) 
    combined_gate.collider = 'box' # Pro jednoduchost a výkon ponechávám box collider na celé bráně
    
    return combined_gate

def create_crematorium(position=(0,0,0), width=30, height=10, depth=20, 
                       base_color=color.hex("#5C5C5C"), roof_color=color.hex("#303030"), 
                       chimney_color=color.hex("#404040"), rotation=(0,0,0)):
    
    crematorium_parts_to_combine = []

    # Hlavní budova (široká, nízká)
    crematorium_parts_to_combine.append(Entity(
        model='cube', 
        scale=(width, height, depth), 
        position=(0, height / 2, 0), 
        color=base_color
    ))

    # Střecha (plochá nebo mírně šikmá, pro jednoduchost plochá)
    roof_thickness = 0.5
    crematorium_parts_to_combine.append(Entity(
        model='cube', 
        scale=(width + 1, roof_thickness, depth + 1), # Mírně přečnívá
        position=(0, height + roof_thickness / 2, 0), 
        color=roof_color
    ))

    # Komín (vysoký a úzký, typicky umístěný vzadu nebo na boku)
    chimney_width = 3
    chimney_height = 25
    chimney_depth = 3
    crematorium_parts_to_combine.append(Entity(
        model='cube', 
        scale=(chimney_width, chimney_height, chimney_depth), 
        position=(width / 2 - chimney_width / 2 - 2, height + chimney_height / 2, depth / 2 - chimney_depth / 2 - 2), # Pozice na rohu střechy
        color=chimney_color
    ))
    
    # Menší "vstupní" část / předsíň (volitelné rozšíření)
    entrance_width = 12
    entrance_depth = 5
    entrance_height = height * 0.7 # Nižší než hlavní budova
    crematorium_parts_to_combine.append(Entity(
        model='cube',
        scale=(entrance_width, entrance_height, entrance_depth),
        position=(0, entrance_height / 2, -depth / 2 - entrance_depth / 2 + 0.5), # Před hlavní budovou
        color=base_color * 0.9 # Trochu jiný odstín
    ))

    # Sloučení všech částí krematoria do jedné entity
    combined_crematorium = Entity(
        model=None, 
        collider='box', # Jednoduchý box collider pro celou budovu
        shader=unlit_shader, 
        position=position,    # Globální pozice
        rotation=rotation     # Globální rotace
    ) 
    
    for part in crematorium_parts_to_combine:
        part.parent = combined_crematorium
        # Pozice částí jsou již relativní k (0,0,0) rodiče
        part.shader = unlit_shader
    
    combined_crematorium.combine() 
    return combined_crematorium

def create_gas_chamber(position=(0,0,0), width=20, height=5, depth=10, 
                       wall_color=color.hex("#383838"), roof_color=color.hex("#252525"), 
                       rotation=(0,0,0)):
    
    gas_chamber_parts_to_combine = []

    # Hlavní budova (plynová komora)
    # Pozice jsou relativní k (0,0,0), což bude střed sloučené entity
    gas_chamber_parts_to_combine.append(Entity(
        model='cube', 
        scale=(width, height, depth), 
        position=(0, height / 2, 0), 
        color=wall_color
    ))

    # Střecha (plochá)
    roof_thickness = 0.3
    gas_chamber_parts_to_combine.append(Entity(
        model='cube', 
        scale=(width + 0.5, roof_thickness, depth + 0.5), # Mírně přečnívá
        position=(0, height + roof_thickness / 2, 0), 
        color=roof_color
    ))

    # Sloučení všech částí plynové komory do jedné entity
    combined_gas_chamber = Entity(
        model=None, 
        collider='box', # Jednoduchý box collider pro celou budovu
        shader=unlit_shader, 
        position=position,    # Globální pozice
        rotation=rotation     # Globální rotace
    ) 
    
    for part in gas_chamber_parts_to_combine:
        part.parent = combined_gas_chamber
        # Pozice částí jsou již relativní k (0,0,0) rodiče
        part.shader = unlit_shader
    
    combined_gas_chamber.combine() 
    return combined_gas_chamber
# --- Vytváření scény s optimalizovanými funkcemi ---
# Všechny statické části scény vytvoříme jako jednu velkou sloučenou entitu,
# abychom minimalizovali počet draw calls.
world_elements = []

# Brána
world_elements.append(create_gate(position=(0, 0, 20)))

# Ploty (X-směr)
world_elements.append(create_fence_segment(start=(3.5, 0, 20), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length
world_elements.append(create_fence_segment(start=(-203.5, 0, 20), length=200 * 2, spacing=2, axis='x')) # Upravil jsem length
# Ploty (Y-směr)
world_elements.append(create_fence_segment(start=(320, 0, 20), length=50 * 2, spacing=2, axis='y')) # Upravil jsem length

# Koleje
world_elements.append(create_rails_segment(start=(0, 0, 0), length=200, spacing=1))
world_elements.append(create_rails_segment(start=(10, 0, 40), length=200, spacing=1))
world_elements.append(create_rails_segment(start=(5, 0, 40), length=200, spacing=1))

# Karanténní domy
for i in range(19):
    pos_x = 25
    world_elements.append(create_simple_house(position=(pos_x + i * 15, 0, 40), width=8, height=3.5, depth=13))
world_elements.append(create_fence_segment(start=(20, 0, 50), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length

# Rodinný Terezínský tábor
count_TRT = 0
for i in range(38):
    pos_x = 25
    if i >= 19:
        world_elements.append(create_simple_house(position=(pos_x + count_TRT * 15, 0, 75), width=8, height=3.5, depth=13))
        count_TRT += 1
    else:
        world_elements.append(create_simple_house(position=(pos_x + i * 15, 0, 60), width=8, height=3.5, depth=13))
world_elements.append(create_fence_segment(start=(20, 0, 85), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length

# Maďarský tábor
count_MT = 0
for i in range(38):
    pos_x = 25
    if i >= 19:
        world_elements.append(create_simple_house(position=(pos_x + count_MT * 15, 0, 110), width=8, height=3.5, depth=13))
        count_MT += 1
    else:
        world_elements.append(create_simple_house(position=(pos_x + i * 15, 0, 95), width=8, height=3.5, depth=13))

# Plot mezi Maďarským táborem a silnicí
world_elements.append(create_fence_segment(start=(20, 0, 120), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length
world_elements.append(create_road_segment(position=(60, 0, 125), length=300, width=6, rotace=90)) # Používáme novou funkci
world_elements.append(create_fence_segment(start=(20, 0, 130), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length

# Mužský tábor
count_MUT = 0
for i in range(38):
    pos_x = 25
    if i >= 19:
        world_elements.append(create_simple_house(position=(pos_x + count_MUT * 15, 0, 155), width=8, height=3.5, depth=13))
        count_MUT += 1
    else:
        world_elements.append(create_simple_house(position=(pos_x + i * 15, 0, 140), width=8, height=3.5, depth=13))
world_elements.append(create_fence_segment(start=(20, 0, 165), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length

# Romský tábor
count_RT = 0
for i in range(38):
    pos_x = 25
    if i >= 19:
        world_elements.append(create_simple_house(position=(pos_x + count_RT * 15, 0, 190), width=8, height=3.5, depth=13))
        count_RT += 1
    else:
        world_elements.append(create_simple_house(position=(pos_x + i * 15, 0, 175), width=8, height=3.5, depth=13))
world_elements.append(create_fence_segment(start=(20, 0, 200), length=150 * 2, spacing=2, axis='x')) # Upravil jsem length

# Věž
world_elements.append(create_tower(position=(10, 0, -20)))

# ženský tabor
count_ZT = 0
count_ZT2=0
for i in range(15):
    pos_x = -20
    pos_y= 20
    if i == 5 or i==10 or i ==15 :
        count_ZT=0
        count_ZT2=count_ZT2+20
    count_ZT=count_ZT+1
    world_elements.append(create_simple_house(position=(pos_x-count_ZT2, 0, pos_y + count_ZT*15), width=8, height=3.5, depth=13, rotation=(0, 90, 0)))

# ženský tabor2
count_ZZT = 0
count_ZZT2=0
for i in range(25):
    pos_x = -90
    pos_y= 20
    if i == 5 or i==10 or i ==15 or i== 15 or i==20:
        count_ZZT=0
        count_ZZT2=count_ZZT2+20
    count_ZZT=count_ZZT+1
    world_elements.append(create_simple_house(position=(pos_x-count_ZZT2, 0, pos_y + count_ZZT*15), width=8, height=3.5, depth=13, rotation=(0, 90, 0)))

world_elements.append(create_fence_segment(start=(-10, 0, 20), length=50 * 2, spacing=2, axis='y'))
world_elements.append(create_fence_segment(start=(15, 0, 20), length=50 * 2, spacing=2, axis='y'))

# ženský tabor B1B
count_ZZTB = 0
count_ZZT2B=0
for i in range(12):
    pos_x = -20
    pos_y= 122
    if i == 4 or i==8 or i ==12 :
        count_ZZTB=0
        count_ZZT2B=count_ZZT2B+20
    count_ZZTB=count_ZZTB+1
    world_elements.append(create_simple_house(position=(pos_x-count_ZZT2B, 0, pos_y + count_ZZTB*15), width=8, height=3.5, depth=13, rotation=(0, 90, 0)))

# ženský tabor B1B2
count_ZZTB3 = 0
count_ZZT2B3=0
for i in range(25):
    pos_x = -50
    pos_y= 122
    if i == 4 or i==8 or i ==12 :
        count_ZZTB3=0
        count_ZZT2B3=count_ZZT2B3+20
    count_ZZTB3=count_ZZTB3+1
    world_elements.append(create_simple_house(position=(pos_x-count_ZZT2B, 0, pos_y + count_ZZTB*15), width=8, height=3.5, depth=13, rotation=(0, 90, 0)))

world_elements.append(create_fence_segment(start=(-10, 0, 20), length=50 * 2, spacing=2, axis='y'))
world_elements.append(create_fence_segment(start=(15, 0, 20), length=50 * 2, spacing=2, axis='y'))


world_elements.append(create_fence_segment(start=(-203.5, 0, 20), length=200 * 2, spacing=2, axis='y'))
world_elements.append(create_fence_segment(start=(15, 0, 20), length=50 * 2, spacing=2, axis='x'))


# --- Sloučení všech statických prvků do jedné hlavní entity ---
# Tímto se výrazně sníží počet draw calls
# Všechny vytvořené entity jsou nyní dětmi 'static_world_objects' a jejich geometrie se sloučí.
# Důležité je, aby si zachovaly své globální pozice, proto se combined_entity.position nemění.
static_world_objects = Entity(model=None, shader=unlit_shader) 

for element in world_elements:
    element.parent = static_world_objects
    # Pokud by element už měl model, chceme, aby si zachoval svou pozici v globálním prostoru
    # a jen se jeho model přenesl do parenta.
    # Protože Ursina combine() pracuje tak, že přenáší relativní pozice,
    # je potřeba, aby dílčí objekty před kombinací měly pozice relativně k rodiči.
    # V mém refaktorování funkcí (create_simple_house atd.) už se o to starám
    # tím, že child entita se nastaví na pozici (0,0,0) a její model se vytvoří na správné lokální pozici.
    # Pokud by to dělalo problémy, je potřeba vypočítat `element.position -= static_world_objects.position`
    # nebo vytvořit `static_world_objects` na (0,0,0) a pak ji přesunout.
    # Aktuální přístup ve funkcích s `part.position -= combined_house.position` by měl fungovat,
    # protože `combined_house` má na začátku pozici (0,0,0) a po combine() se její model vyrenderuje na správném místě.

static_world_objects.combine()
# Nastavte kolider pro celou sloučenou scénu. 'box' je jednodušší, MeshCollider přesnější ale náročnější.
# MeshCollider pro takto velkou a složitou scénu může být stále příliš náročný.
# Collider by měl být na 'ground' nebo na jednotlivých důležitých entitách před sloučením.
# Po sloučení všech do jedné entity je efektivnější mít kolize řešené buď na groundu,
# nebo na jednotlivých původních sloučených celcích (např. jeden collider na dům, jeden na úsek plotu).
# Pokud potřebuješ, aby se hráč srážel se všemi těmito objekty,
# bude nejlepší ponechat kolidery na sloučených entitách jako `combined_house`, `combined_fence` atd.
# Tím se vyhýbáš tisícům koliderů, ale stále máš kolize.
# Takže jsem kolidery ve funkcích `create_*` ponechal u sloučených entit.


app.run()