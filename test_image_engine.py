import io
import unittest
from PIL import Image
import image_engine

class ImageEngineTests(unittest.TestCase):
    def setUp(self):
        im=Image.new("RGB",(320,240),(120,80,40))
        b=io.BytesIO(); im.save(b,"PNG"); self.data=b.getvalue()

    def test_info(self):
        info=image_engine.image_info(self.data)
        self.assertEqual((info["width"],info["height"]),(320,240))

    def test_resize(self):
        out=image_engine.resize_image(self.data,160,120,"PNG")
        info=image_engine.image_info(out)
        self.assertEqual((info["width"],info["height"]),(160,120))

    def test_convert(self):
        out=image_engine.convert_image(self.data,"JPEG")
        self.assertEqual(image_engine.image_info(out)["format"],"JPEG")

    def test_transform(self):
        out=image_engine.transform_image(self.data,0,0,0,0,90,"None")
        info=image_engine.image_info(out)
        self.assertEqual((info["width"],info["height"]),(240,320))

if __name__=="__main__":
    unittest.main()
