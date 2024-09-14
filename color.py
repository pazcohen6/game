"""
Color definitions for use in the game.

Colors are represented as tuples of RGB values.
"""
white = (0xFF, 0xFF, 0xFF)
black = (0x0, 0x0, 0x0)
red = (0xFF, 0x0, 0x0)

player_atk = (0xE0, 0xE0, 0xE0)
enemy_atk = (0xFF, 0xC0, 0xC0)
needs_target = (0x3F, 0XFF, 0XFF)
status_effect_applied = (0x3F, 0xFF, 0x3F)
descend = (0x9F, 0x3F, 0xFF)

player_die = (0xFF, 0x30, 0x30)
enemy_die = (0xFF, 0xA0, 0x30)

invalid = (0xFF, 0xFF, 0x00)
impossible = (0x80, 0x80, 0x80)
error = (0xFF, 0x40, 0x40)

welcome_text = (0x20, 0xA0, 0xFF)
health_recoverd = (0x00, 0xFF, 0x00)

bar_text = white
bar_filled = (0x0, 0x60, 0x0)
bar_empty = (0x40, 0x10, 0x10)

# menu
menu_title = (255,255,63)
menu_text = white