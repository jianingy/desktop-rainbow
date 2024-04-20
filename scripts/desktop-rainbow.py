import requests
import sys
import click
import webcolors
import time

@click.group()
@click.option('--server', default='localhost', help='Server address')
@click.pass_context
def cli(ctx, server):
    ctx.ensure_object(dict)
    ctx.obj['api_url'] = f'http://{server}/api/hue'

def get_color_rgb(color):
    if color.find(',') == -1:
        return tuple(webcolors.name_to_rgb(color))
    else:
        return map(int, color.split(','))

def set_light(api_url, light_id, rgb):
    params = {
        'id': light_id,
        'color': ','.join(map(str, list(rgb)))
    }
    if light_id == -1:
        params.pop('id')

    return requests.get(api_url, params=params)

def interpolate_color(start_color, end_color, steps):
    # Extract RGB components from start and end colors
    start_red, start_green, start_blue = start_color
    end_red, end_green, end_blue = end_color

    # Calculate step sizes for each component
    red_step = (end_red - start_red) / steps
    green_step = (end_green - start_green) / steps
    blue_step = (end_blue - start_blue) / steps

    # Generate gradient colors
    gradient_colors = []
    for i in range(steps + 1):
        # Interpolate each component
        red = int(start_red + i * red_step)
        green = int(start_green + i * green_step)
        blue = int(start_blue + i * blue_step)
        # Add interpolated color to the gradient
        gradient_colors.append((red, green, blue))

    return gradient_colors

@cli.command()
@click.option('--start', default='0', help='Light id')
@click.pass_context
def rainbow(ctx, start):
    api_url = ctx.obj['api_url']
    start = int(start)
    for i in range(36):
        if i % 3 == start:
            set_light(api_url, i, (255, 0, 0))
        elif i % 3 == start + 1:
            set_light(api_url, i, (0, 255, 0))
        else:
            set_light(api_url, i, (0, 0, 255))

@cli.command()
@click.pass_context
@click.option('--color', default='255,255,255', help='RGB color')
@click.option('--id', default='-1', help='Light id')
def set_color(ctx, color, id):
    api_url = ctx.obj['api_url']    
    set_light(api_url, int(id), get_color_rgb(color))

@cli.command()
@click.pass_context
@click.option('--start', default='255,255,255', help='Start RGB color')
@click.option('--end', default='0,0,0', help='End RGB color')
@click.option('--step', default='50', help='Steps')
def gradient(ctx, start, end, step):
    api_url = ctx.obj['api_url']
    colors = interpolate_color(get_color_rgb(start), get_color_rgb(end), int(step))
    for color in colors:
        set_light(api_url, -1, color)

@cli.command()
@click.pass_context
@click.option('--start', default='255,255,255', help='Start RGB color')
@click.option('--end', default='0,0,0', help='End RGB color')
@click.option('--step', default='50', help='Steps')
def breeze(ctx, start, end, step):
    api_url = ctx.obj['api_url']
    colors = interpolate_color(get_color_rgb(start), get_color_rgb(end), int(step))
    while True:
        for color in colors:
            set_light(api_url, -1, color)
            time.sleep(0)
        for color in reversed(colors):
            set_light(api_url, -1, color)        
            time.sleep(0)            
        time.sleep(1)
    
if __name__ == '__main__':
    cli()