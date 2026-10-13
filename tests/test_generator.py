"""Unit tests for MemeCP generator (compatible with pytest and python -m unittest)."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from memecp.generator import (
    create_classic_meme,
    create_demotivator,
    create_post_ironic_meme,
    create_caption_meme,
    create_news_meme,
    list_available_fonts,
    load_image,
    resolve_font_path,
)


class TestMemeGenerator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.sample_img_path = self.tmp_dir / "sample.png"
        im = Image.new("RGB", (600, 400), color=(80, 140, 200))
        im.save(self.sample_img_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_list_fonts(self):
        fonts = list_available_fonts()
        self.assertIn("impact", fonts)
        self.assertIn("serif", fonts)
        self.assertIn("sans", fonts)
        self.assertIn("lobster", fonts)
        self.assertIn("oswald", fonts)
        self.assertIn("futura", fonts)
        self.assertIn("caption", fonts)

    def test_resolve_font_path(self):
        p = resolve_font_path("impact")
        self.assertTrue(p.exists())
        self.assertTrue(p.name.endswith((".ttf", ".otf")))

    def test_load_image_local(self):
        img = load_image(str(self.sample_img_path))
        self.assertEqual(img.size, (600, 400))
        self.assertEqual(img.mode, "RGB")

    def test_create_classic_meme(self):
        out_file = self.tmp_dir / "classic.jpg"
        res = create_classic_meme(
            image_source=str(self.sample_img_path),
            top_text="HELLO WORLD",
            bottom_text="TESTING BOTTOM TEXT",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertEqual(res["width"], 600)
        self.assertEqual(res["height"], 400)

    def test_create_classic_meme_cyrillic(self):
        out_file = self.tmp_dir / "classic_cyrillic.jpg"
        res = create_classic_meme(
            image_source=str(self.sample_img_path),
            top_text="ВЕРХНИЙ ТЕКСТ",
            bottom_text="НИЖНИЙ ТЕКСТ ДЛЯ ПРОВЕРКИ",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())

    def test_create_demotivator(self):
        out_file = self.tmp_dir / "demotivator.jpg"
        res = create_demotivator(
            image_source=str(self.sample_img_path),
            title="ДЕМОТИВАТОР",
            subtitle="ОБЪЯСНИТЕЛЬНАЯ БРИГАДА УЖЕ В ПУТИ",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertGreater(res["width"], 600)
        self.assertGreater(res["height"], 400)

    def test_create_caption_meme(self):
        out_file = self.tmp_dir / "caption.jpg"
        res = create_caption_meme(
            image_source=str(self.sample_img_path),
            caption="violence",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertEqual(res["width"], 600)
        self.assertGreater(res["height"], 400)

    def test_create_post_ironic_caption_box(self):
        out_file = self.tmp_dir / "caption_box.jpg"
        res = create_post_ironic_meme(
            image_source=str(self.sample_img_path),
            caption="Когда написал код и тесты прошли с первого раза",
            style="caption_box",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertGreater(res["height"], 400)

    def test_create_post_ironic_deep_fry(self):
        out_file = self.tmp_dir / "deepfry.jpg"
        res = create_post_ironic_meme(
            image_source=str(self.sample_img_path),
            caption="БАЗА",
            style="deep_fry",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())

    def test_create_news_meme(self):
        out_file = self.tmp_dir / "news.jpg"
        res = create_news_meme(
            image_source=str(self.sample_img_path),
            headline="Мемы были официально признаны искусством",
            category="НОВОСТИ",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertEqual(res["width"], 600)
        self.assertEqual(res["height"], 400)

    def test_create_news_meme_long_headline(self):
        out_file = self.tmp_dir / "news_long.jpg"
        res = create_news_meme(
            image_source=str(self.sample_img_path),
            headline="Голубь официально признан ведущим системным инженером компании после успешного деплоя всей инфраструктуры",
            category="⚡ СРОЧНО",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["path"]).exists())
        self.assertEqual(res["width"], 600)
        self.assertEqual(res["height"], 400)


if __name__ == "__main__":
    unittest.main()
