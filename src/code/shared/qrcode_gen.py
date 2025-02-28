import qrcode
from PIL import Image, ImageDraw, ImageFont
import re

def make_qrc(data, caption, caption2, boxsize, color_text='black'):
    qr = qrcode.make(data, box_size=boxsize)
    width, height = qr.size
    bi = Image.new('RGBA', (width + 10, height + (height // 5)), 'white')
    bi.paste(qr, (5, 5, (width + 5), (height + 5)))
    if boxsize >= 5:
        fontsize = boxsize * (80/15)
    else:
        fontsize = 2 * (80/15)
    #fontsize = boxsize * (70/15)
    Imfont = ImageFont.truetype("arial.ttf", int(fontsize))
    # add if-then for captions with _ 
    # everything after _ are called optional suffix in the BOS naming/labelling guide v1.3
    # regex for the two groups enclosed in separate ( and ) bracket and separated by _
    result = re.search(r"(.*)_(.*)", caption)
    resultFinal = caption if result is None else result

    caption = (resultFinal if result is None else result.group(1))
    caption2a = (caption2 if result is None else result.group(2))
        
    w, h = Imfont.getsize(caption)
    # set also the 2nd line for caption 2, if any
    if caption2a is not None:
        w2, h2 = Imfont.getsize(caption2a)
    draw = ImageDraw.Draw(bi)
    draw.text(((width - w + 5) / 2, (height + ((height / 15) - h) / 2)), caption, font=Imfont, fill=color_text)
    # split the caption into 2 lines and draw center
    if caption2a is not None:
        print('caption2a %s' %(caption2a))
        draw.text(((width - w2 + 5) / 2, (height + ((height / 15) + h2) / 2)), caption2a, font=Imfont, fill=color_text)

    return bi
