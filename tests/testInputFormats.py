import os
import tempfile
import unittest

import pymupdf
from PIL import Image

from DotToDot import getOutputPaths, loadInputImage
from Main import parseArguments


class TestInputFormats(unittest.TestCase):

    def testLoadsJpgAndPngImages(self):
        with tempfile.TemporaryDirectory() as directory:
            for extension in ('.jpg', '.png'):
                path = os.path.join(directory, 'input' + extension)
                Image.new('RGB', (12, 8), 'white').save(path)

                loaded = loadInputImage(path)

                self.assertEqual(loaded.size, (12, 8))
                self.assertEqual(loaded.mode, 'RGB')

    def testLoadsFirstPdfPage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'input.pdf')
            with pymupdf.open() as document:
                document.new_page(width=72, height=48)
                document.save(path)

            loaded = loadInputImage(path, pdfDpi=72)

            self.assertEqual(loaded.size, (72, 48))
            self.assertEqual(loaded.mode, 'RGB')

    def testLoadsPdfAtRequestedResolution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'input.pdf')
            with pymupdf.open() as document:
                document.new_page(width=72, height=48)
                document.save(path)

            loaded = loadInputImage(path, pdfDpi=144)

            self.assertEqual(loaded.size, (144, 96))

    def testParserAcceptsSupportedInputTypes(self):
        with tempfile.TemporaryDirectory() as directory:
            for extension in ('.jpg', '.jpeg', '.png', '.pdf'):
                path = os.path.join(directory, 'input' + extension)
                open(path, 'wb').close()

                arguments = parseArguments([path])

                self.assertEqual(arguments.input_file, path)

    def testParserAcceptsQualityOptions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'input.pdf')
            open(path, 'wb').close()

            arguments = parseArguments([
                path,
                '--max-dots', '1600',
                '--max-dimension', '1800',
                '--pdf-dpi', '300'])

            self.assertEqual(arguments.max_dots, 1600)
            self.assertEqual(arguments.max_dimension, 1800)
            self.assertEqual(arguments.pdf_dpi, 300)

    def testParserRejectsUnsupportedInputType(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'input.gif')
            open(path, 'wb').close()

            with self.assertRaises(SystemExit):
                parseArguments([path])

    def testParserRejectsTracingDimensionBelowMinimum(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'input.png')
            open(path, 'wb').close()

            with self.assertRaises(SystemExit):
                parseArguments([path, '--max-dimension', '399'])

    def testOutputPathsUseExpectedFileTypes(self):
        self.assertEqual(
            getOutputPaths('source/example.png'),
            ('out/jpg/example.jpg', 'out/pdf/example.pdf'))


if __name__ == '__main__':
    unittest.main()