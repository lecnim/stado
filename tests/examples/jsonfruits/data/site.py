from stado import run, layout, permalink

layout('fruits.json', 'layout.mustache')
permalink('fruits.json', 'fruits.html')

run()