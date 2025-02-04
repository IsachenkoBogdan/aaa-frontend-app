from aiohttp.web import Response
from aiohttp.web import View
from aiohttp_jinja2 import render_template

from lib.image import image_to_img_src
from lib.image import PolygonDrawer
from lib.image import open_image
from lib.image import image_to_numpy


class IndexView(View):
    async def get(self) -> Response:
        return render_template("index.html", self.request, {})

    async def post(self) -> Response:
        try:
            form = await self.request.post()
            draw = PolygonDrawer(open_image(form["image"].file))
            model = self.request.app["model"]
            words = []
            try:
                min_accuracy = int(form["min_accuracy"]) / 100
            except Exception:
                min_accuracy = 0
            image_np = image_to_numpy(form["image"].file)
            for coords, word, accuracy in model.readtext(image_np):
                if accuracy > min_accuracy:
                    draw.highlight_word(coords, word)
                    cropped_img = draw.crop(coords)
                    cropped_img_b64 = image_to_img_src(cropped_img)
                    words.append(
                        {
                            "image": cropped_img_b64,
                            "word": word,
                            "accuracy": accuracy, }
                    )
            image_b64 = image_to_img_src(draw.get_highlighted_image())
            ctx = {"image": image_b64, "words": words}
        except Exception as err:
            ctx = {"error": str(err)}
        return render_template("index.html", self.request, ctx)
