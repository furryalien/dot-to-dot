# dot-to-dot
Converts images into full dot to dot puzzles.

Read more about the project **[here](https://medium.com/@oliverstenbom/worlds-largest-dot-to-dot-4babe597dfeb)**

To use, clone the repository with `git clone https://github.com/ostenbom/dot-to-dot.git`, install requirements (you'll particularly need a Cairo binding like cairocffi and Pillow). Then run:

```
python Main.py path/to/image.jpg
```

Supported input formats are JPG, PNG, and PDF. For PDF input, the first page is
used to create the puzzle.

Increase the detail level with the optional quality controls:

```
python Main.py path/to/image.pdf --max-dots 1600 --max-dimension 1800 --pdf-dpi 300
```

Higher values preserve more detail but take longer to process. `--pdf-dpi`
controls how sharply a PDF page is rendered before tracing, while
`--max-dimension` controls the tracing resolution.

If you'd like to know more about how it works, reading DotToDot.py is a good start! Also the medium article I wrote, more documentation coming soon.
