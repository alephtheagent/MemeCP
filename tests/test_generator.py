"""Unit tests for MemeCP generator (compatible with pytest and python -m unittest)."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

from memecp.generator import (
    create_classic_meme,
    create_demotivator,
    create_post_ironic_meme,
    create_caption_meme,
    create_news_meme,
    list_available_fonts,
    load_image,
    load_media,
    resolve_font_path,
    resolve_output_path,
)


class TestMemeGenerator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.sample_img_path = self.tmp_dir / "sample.png"
        im = Image.new("RGB", (600, 400), color=(80, 140, 200))
        im.save(self.sample_img_path)

        # Create multi-frame animated GIF sample
        self.sample_gif_path = self.tmp_dir / "sample_animated.gif"
        gif_frames = []
        for i, color in enumerate([
            (220, 50, 50),
            (50, 200, 50),
            (50, 100, 220),
            (230, 180, 20),
        ]):
            frame = Image.new("RGB", (400, 300), color=color)
            d = ImageDraw.Draw(frame)
            d.rectangle([40 + i * 10, 40, 100 + i * 10, 100], fill=(255, 255, 255))
            gif_frames.append(frame.convert("P", palette=Image.ADAPTIVE))

        gif_frames[0].save(
            self.sample_gif_path,
            format="GIF",
            save_all=True,
            append_images=gif_frames[1:],
            duration=120,
            loop=0,
            disposal=2,
        )

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

    def test_load_media_animated(self):
        media = load_media(str(self.sample_gif_path))
        self.assertTrue(media.is_animated)
        self.assertEqual(len(media.frames), 4)
        self.assertEqual(media.width, 400)
        self.assertEqual(media.height, 300)

    def test_resolve_output_path_extensions(self):
        # Static defaults to .jpg
        p_static = resolve_output_path(None, prefix="classic", is_gif=False)
        self.assertTrue(str(p_static).endswith(".jpg"))

        # Animated defaults to .gif
        p_gif = resolve_output_path(None, prefix="classic", is_gif=True)
        self.assertTrue(str(p_gif).endswith(".gif"))

        # Animated replaces .jpg with .gif
        custom_jpg = str(self.tmp_dir / "meme.jpg")
        p_converted = resolve_output_path(custom_jpg, prefix="classic", is_gif=True)
        self.assertTrue(str(p_converted).endswith(".gif"))

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

    def test_create_classic_meme_animated_gif(self):
        out_file = self.tmp_dir / "classic_animated.gif"
        res = create_classic_meme(
            image_source=str(self.sample_gif_path),
            top_text="ВЕРХНИЙ ТЕКСТ",
            bottom_text="ГИФКА ДВИЖЕТСЯ",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        p = Path(res["path"])
        self.assertTrue(p.exists())
        self.assertEqual(p.suffix.lower(), ".gif")

        # Verify animated GIF validity and frame count
        with Image.open(p) as img:
            self.assertTrue(getattr(img, "is_animated", False))
            self.assertGreater(getattr(img, "n_frames", 1), 1)
            self.assertEqual(img.size, (400, 300))

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

    def test_create_demotivator_animated_gif(self):
        out_file = self.tmp_dir / "demotivator_animated.gif"
        res = create_demotivator(
            image_source=str(self.sample_gif_path),
            title="АНИМИРОВАННЫЙ ДЕМОТИВАТОР",
            subtitle="ОН РЕАЛЬНО АНИМИРОВАННЫЙ",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        p = Path(res["path"])
        self.assertTrue(p.exists())
        self.assertEqual(p.suffix.lower(), ".gif")

        with Image.open(p) as img:
            self.assertTrue(getattr(img, "is_animated", False))
            self.assertGreater(getattr(img, "n_frames", 1), 1)
            self.assertGreater(img.width, 400)
            self.assertGreater(img.height, 300)

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

    def test_create_caption_meme_animated_gif(self):
        out_file = self.tmp_dir / "caption_animated.gif"
        res = create_caption_meme(
            image_source=str(self.sample_gif_path),
            caption="me when the animated gif meme works perfectly",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        p = Path(res["path"])
        self.assertTrue(p.exists())
        self.assertEqual(p.suffix.lower(), ".gif")

        with Image.open(p) as img:
            self.assertTrue(getattr(img, "is_animated", False))
            self.assertGreater(getattr(img, "n_frames", 1), 1)
            self.assertEqual(img.width, 400)
            self.assertGreater(img.height, 300)

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

    def test_create_post_ironic_deep_fry_animated(self):
        out_file = self.tmp_dir / "deepfry_animated.gif"
        res = create_post_ironic_meme(
            image_source=str(self.sample_gif_path),
            caption="ЯДЕРНЫЙ СВЕТ",
            style="deep_fry",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        p = Path(res["path"])
        self.assertTrue(p.exists())
        with Image.open(p) as img:
            self.assertTrue(getattr(img, "is_animated", False))
            self.assertGreater(getattr(img, "n_frames", 1), 1)

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

    def test_create_news_meme_animated_gif(self):
        out_file = self.tmp_dir / "news_animated.gif"
        res = create_news_meme(
            image_source=str(self.sample_gif_path),
            headline="Срочные новости: GIF мемы теперь работают",
            category="⚡ СРОЧНО",
            output_path=str(out_file),
        )
        self.assertTrue(res["success"])
        p = Path(res["path"])
        self.assertTrue(p.exists())
        with Image.open(p) as img:
            self.assertTrue(getattr(img, "is_animated", False))
            self.assertGreater(getattr(img, "n_frames", 1), 1)
            self.assertEqual(img.width, 400)
            self.assertEqual(img.height, 300)

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
