from django.http import HttpResponse
from PIL import Image, ImageDraw
import io


def makeimage_alt(request):

    width = request.GET.get("width")
    height = request.GET.get("height")
    text = request.GET.get("text", "")

    try:
        width = int(width)
        height = int(height)

        if width < 10 or width > 2000:
            raise ValueError

        if height < 10 or height > 2000:
            raise ValueError

    except:
        return HttpResponse(
            "Invalid image size",
            status=400
        )

    image = Image.new(
        "RGB",
        (width, height),
        color=(220,220,220)
    )

    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0,0), text)

    text_width = bbox[2]-bbox[0]
    text_height = bbox[3]-bbox[1]

    x=(width-text_width)//2
    y=(height-text_height)//2

    draw.text((x,y), text, fill="black")

    buffer=io.BytesIO()

    image.save(
        buffer,
        "JPEG"
    )

    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/jpeg"
    )