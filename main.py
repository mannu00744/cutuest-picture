from __future__ import annotations
import math, os, struct, zlib

# A tiny, self-contained raster illustrator for the make.fun picture contest.
# It writes the same hand-drawn-style PNG on every run using only Python's stdlib.
S = 2
W = H = 512
CW = CH = W * S
pixels = bytearray(CW * CH * 3)

def rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend_pixel(x, y, color):
    if 0 <= x < CW and 0 <= y < CH:
        i = (y * CW + x) * 3
        pixels[i:i+3] = bytes(color)

def ellipse(cx, cy, rx, ry, color, outline=None, width=3):
    cx, cy, rx, ry, width = [int(round(v*S)) for v in (cx, cy, rx, ry, width)]
    col = rgb(color)
    edge = rgb(outline) if outline else None
    x0, x1 = max(0, cx-rx-width-1), min(CW, cx+rx+width+1)
    y0, y1 = max(0, cy-ry-width-1), min(CH, cy+ry+width+1)
    for y in range(y0, y1):
        dy = (y-cy) / max(1, ry)
        for x in range(x0, x1):
            dx = (x-cx) / max(1, rx)
            d = dx*dx + dy*dy
            if d <= 1:
                blend_pixel(x, y, col)
            elif edge and d <= (1 + width/max(1, min(rx, ry)))**2:
                blend_pixel(x, y, edge)

def line(points, color, width=4):
    col = rgb(color); r = max(1, width*S/2)
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        ax*=S; ay*=S; bx*=S; by*=S
        steps = int(max(abs(bx-ax), abs(by-ay))) + 1
        for n in range(steps+1):
            t = n/max(1, steps); x = ax+(bx-ax)*t; y = ay+(by-ay)*t
            x0, x1 = int(x-r-1), int(x+r+1); y0, y1 = int(y-r-1), int(y+r+1)
            for py in range(max(0,y0), min(CH,y1)):
                for px in range(max(0,x0), min(CW,x1)):
                    if (px-x)**2 + (py-y)**2 <= r*r: blend_pixel(px,py,col)

def polygon(points, color, outline=None, width=3):
    col = rgb(color)
    pts = [(int(x*S), int(y*S)) for x,y in points]
    x0=max(0,min(x for x,y in pts)); x1=min(CW,max(x for x,y in pts)+1)
    y0=max(0,min(y for x,y in pts)); y1=min(CH,max(y for x,y in pts)+1)
    for py in range(y0,y1):
        for px in range(x0,x1):
            inside=False; j=len(pts)-1
            for i,(xi,yi) in enumerate(pts):
                xj,yj=pts[j]
                if ((yi>py)!=(yj>py)) and px < (xj-xi)*(py-yi)/(yj-yi+1e-9)+xi:
                    inside=not inside
                j=i
            if inside: blend_pixel(px,py,col)
    if outline:
        line(points+[points[0]], outline, width)

def downsample():
    out=bytearray(W*H*3)
    for y in range(H):
        for x in range(W):
            sums=[0,0,0]
            for sy in range(S):
                for sx in range(S):
                    i=((y*S+sy)*CW+(x*S+sx))*3
                    for c in range(3): sums[c]+=pixels[i+c]
            j=(y*W+x)*3
            out[j:j+3]=bytes(v//(S*S) for v in sums)
    return out

def png_chunk(kind, data):
    body=kind+data
    return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)

def save_png(path):
    image=downsample()
    raw=b''.join(b'\0'+image[y*W*3:(y+1)*W*3] for y in range(H))
    payload=b'\x89PNG\r\n\x1a\n'
    payload+=png_chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
    payload+=png_chunk(b'IDAT',zlib.compress(raw,9))+png_chunk(b'IEND',b'')
    with open(path,'wb') as f: f.write(payload)

# Soft apricot sky and a simple pool of light under the character.
for y in range(CH):
    t=y/(CH-1); c0=rgb('#f7c9b7'); c1=rgb('#ffe9c7')
    c=tuple(int(a*(1-t)+b*t) for a,b in zip(c0,c1))
    for x in range(CW): blend_pixel(x,y,c)
ellipse(256,214,184,176,'#ffdfbd')
ellipse(256,458,132,18,'#e9a995')
# Two tiny floating sparkles keep the background airy.
for x,y in [(96,142),(414,186),(377,99),(122,273)]:
    line([(x,y-8),(x,y+8)],'#fff8e8',3); line([(x-7,y),(x+7,y)],'#fff8e8',3)

ink='#65463e'; cream='#fff0d4'; honey='#c98657'; pink='#f39b9d'
# Bear ears, with warm inner fur.
ellipse(181,191,54,61,ink); ellipse(181,190,48,55,honey); ellipse(184,194,28,37,'#f4b2a0')
ellipse(331,191,54,61,ink); ellipse(331,190,48,55,honey); ellipse(328,194,28,37,'#f4b2a0')
# Round body and tiny tucked paws.
ellipse(256,330,118,129,ink); ellipse(256,326,111,123,honey)
ellipse(204,411,39,30,ink); ellipse(204,406,34,25,cream)
ellipse(308,411,39,30,ink); ellipse(308,406,34,25,cream)
ellipse(256,366,64,67,'#eeb98f')
# Head, broad cheeks and soft muzzle.
ellipse(256,252,135,117,ink); ellipse(256,247,128,110,cream)
ellipse(167,276,37,27,'#ffe5d0'); ellipse(345,276,37,27,'#ffe5d0')
# Big glassy eyes with warm irises and clear highlights.
ellipse(211,246,25,31,ink); ellipse(211,246,20,27,'#48352f')
ellipse(301,246,25,31,ink); ellipse(301,246,20,27,'#48352f')
ellipse(205,237,7,9,'#ffffff'); ellipse(295,237,7,9,'#ffffff')
ellipse(216,255,3,4,'#d89b72'); ellipse(306,255,3,4,'#d89b72')
# Button nose, smile, rosy cheeks.
ellipse(256,277,10,7,'#7a5046'); line([(256,283),(256,290),(247,296)],ink,3); line([(256,290),(265,296)],ink,3)
ellipse(178,286,15,8,pink); ellipse(334,286,15,8,pink)
# A tiny jaunty daisy tucked by one ear.
for a in range(0,360,60):
    r=math.radians(a); ellipse(328+13*math.cos(r),139+13*math.sin(r),8,11,'#fffdf3')
ellipse(328,139,7,7,'#f6c65d')
line([(328,151),(333,174),(345,187)],'#72956b',3)

# Tea cup handle and cup foreground, a cozy little nest.
ellipse(379,371,37,49,'#fff0d4',ink,6); ellipse(379,371,20,31,'#ffe2c8')
polygon([(159,371),(353,371),(334,454),(179,454)],'#f28d83',ink,5)
ellipse(256,372,99,22,'#ffe9d2',ink,5)
ellipse(256,380,82,13,'#c88768')
# Cup decoration and a final highlight.
line([(204,417),(228,424),(249,417),(270,424),(294,417)],'#ffe6d5',4)
ellipse(256,434,8,7,'#fff3db')
# Tiny paws curl over the cup lip, making the bear look cozily tucked in.
ellipse(218,370,18,13,cream,ink,3); ellipse(294,370,18,13,cream,ink,3)
line([(212,371),(216,375)],'#d59d79',2); line([(220,371),(224,375)],'#d59d79',2)
line([(288,371),(292,375)],'#d59d79',2); line([(296,371),(300,375)],'#d59d79',2)

out_dir=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
os.makedirs(out_dir,exist_ok=True)
save_png(os.path.join(out_dir,'entry.png'))

