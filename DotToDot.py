import os
import time
import pymupdf
from PIL import Image

from EdgeDetector import EdgeDetector
from EdgeMatrix import EdgeMatrix
from EdgeFollower import EdgeFollower
from TraceConverter import TraceConverter
from LineConnector import LineConnector
from DotCleanup import DotCleanup

from OutputImage import OutputImage
from OutputNonConnectedLines import OutputNonConnectedLines
from IntermediateImage import IntermediateImage

TEMP_IMG_NAME = "temp_img.jpg"
GREEDY_SOLUTIONS_TO_TRY = 50
MIN_INPUT_DIMENSION = 400
INPUT_DIMENSION_STEP = 200

def loadInputImage(fullFilePath, pdfDpi=300):
    if os.path.splitext(fullFilePath)[1].lower() == '.pdf':
        with pymupdf.open(fullFilePath) as document:
            if document.page_count == 0:
                raise ValueError('PDF contains no pages: ' + fullFilePath)
            pixmap = document[0].get_pixmap(dpi=pdfDpi, alpha=False)
            return Image.frombytes(
                'RGB', (pixmap.width, pixmap.height), pixmap.samples)

    with Image.open(fullFilePath) as image:
        return image.convert('RGB')

def getOutputPaths(fullFilePath):
    fileName = os.path.splitext(os.path.split(fullFilePath)[-1])[0]
    return 'out/jpg/' + fileName + '.jpg', 'out/pdf/' + fileName + '.pdf'

def timeFunction(function, *args):
    start = time.perf_counter()
    returnValue = function(*args)
    end = time.perf_counter()
    print ('--- ' + str(function.__name__) + ' --- Time: ' + str(end - start) + ' ---')
    return returnValue

def makeDotToDot(fullFilePath, intermediateSteps = False):
    # Getting proper in/out names and image dimensions.
    outPathJpg, outPathPdf = getOutputPaths(fullFilePath)
    os.makedirs(os.path.dirname(outPathJpg), exist_ok=True)
    os.makedirs(os.path.dirname(outPathPdf), exist_ok=True)

    imageData = loadInputImage(fullFilePath)
    width = imageData.width
    height = imageData.height

    # Canny edge detection step
    edgeDetector = EdgeDetector(imageData)
    edgesNumberMatrix = timeFunction(edgeDetector.getCannyEdges)

    edgeMatrix = EdgeMatrix(edgesNumberMatrix)

    if intermediateSteps:
        outCanny = IntermediateImage([edgeMatrix.points], width, height)
        outCanny.colorWhiteSegments()
        outCanny.saveImage("intermediate/canny.jpg")

    # Trace following step
    edgeFollower = EdgeFollower(edgeMatrix, width, height)
    traces = timeFunction(edgeFollower.getTraces)

    if intermediateSteps:
        outEdges = IntermediateImage(traces, width, height)
        outEdges.colorAllSegments()
        outEdges.saveImage("intermediate/edges.jpg")

    # Trace to line conversion
    traceConverter = TraceConverter(traces)
    lines = timeFunction(traceConverter.getLines)

    if intermediateSteps:
        nonConnectedLinesOut = OutputNonConnectedLines(lines, width, height)
        nonConnectedLinesOut.saveImage("intermediate/lines.jpg")

    print ('Lines to connect: ' + str(len(lines)))

    # Finding the best greedy solution
    lineConnector = LineConnector(lines)
    greedyLines = timeFunction(lineConnector.bestOfManyGreedys, GREEDY_SOLUTIONS_TO_TRY)
    greedyPoints = [point for sublist in greedyLines for point in sublist]

    if intermediateSteps:
            outGreedy = OutputImage(greedyPoints, width, height, True, False, "intermediate/notClean.pdf", "intermediate/notClean.jpg")

    # Cleaning up too close/far away dots
    print ('Dots before clean: ' + str(len(greedyPoints)))
    dotCleaner = DotCleanup(greedyPoints, width, height)
    cleanPoints = timeFunction(dotCleaner.getCleanedDots)
    dotsInImage = len(cleanPoints)

    # Output image
    print ('Dots in image: ' + str(dotsInImage))
    out = OutputImage(cleanPoints, width, height, True, False, outPathPdf)
    out.saveImage(outPathJpg)

    return cleanPoints

def makeMaxSizeDot(fullFilePath, maxDots, maxInputDimension=1200, pdfDpi=300):
    inputImageDimension = maxInputDimension
    dotsInImage = maxDots + 1

    outPathJpg, outPathPdf = getOutputPaths(fullFilePath)

    # Repeat complete makeDotToDot process, decreasing image resolution, until
    # few enough dots
    while(dotsInImage > maxDots and inputImageDimension >= MIN_INPUT_DIMENSION):
        print('Image Dimensions now at: ' + str(inputImageDimension))
        imageData = loadInputImage(fullFilePath, pdfDpi)
        width = imageData.width
        height = imageData.height
        maxDimension = width if width > height else height
        if (maxDimension > inputImageDimension):
            scaling = float(inputImageDimension) / maxDimension
            width = int(width * scaling)
            height = int(height * scaling)
            imageData = imageData.resize((width, height), Image.Resampling.BICUBIC)

        imageData.save(TEMP_IMG_NAME)

        dotPoints = makeDotToDot(TEMP_IMG_NAME)
        dotsInImage = len(dotPoints)
        inputImageDimension -= INPUT_DIMENSION_STEP

    OutputImage(dotPoints, width, height, True, False, outPathPdf, outPathJpg)

    temporaryOutputs = [
        TEMP_IMG_NAME,
        os.path.join('out', 'jpg', TEMP_IMG_NAME),
        os.path.join('out', 'pdf', os.path.splitext(TEMP_IMG_NAME)[0] + '.pdf')]
    for temporaryOutput in temporaryOutputs:
        if os.path.exists(temporaryOutput):
            os.remove(temporaryOutput)
