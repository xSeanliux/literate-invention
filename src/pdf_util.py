import fitz
import PyPDF2

file_path = "pdfs/goldenretriever.pdf"

rgb_scale = 255
cmyk_scale = 100


def rgb_to_cmyk(x):
    #https://stackoverflow.com/questions/14088375/how-can-i-convert-rgb-to-cmyk-and-vice-versa-in-python

    r, g, b = x[0], x[1], x[2]
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / float(rgb_scale)
    m = 1 - g / float(rgb_scale)
    y = 1 - b / float(rgb_scale)

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) 
    m = (m - min_cmy) 
    y = (y - min_cmy) 
    k = min_cmy

    # rescale to the range [0,cmyk_scale]
    return (round(c*cmyk_scale, 4), round(m*cmyk_scale, 4), round(y*cmyk_scale, 4), round(k*cmyk_scale, 4))

def get_page_dimensions(file_path):
    # returns width and height in mm

    page_dimensions = []

    pdf = PyPDF2.PdfReader(file_path, "rb")

    for p in pdf.pages:
        # w_in_user_space_units = p.mediaBox.getWidth()
        # h_in_user_space_units = p.mediaBox.getHeight()

        # 1 user space unit is 1/72 inch
        # 1/72 inch ~ 0.352 millimeters

        w = float(p.mediabox.width) * 0.352
        h = float(p.mediabox.height) * 0.352
        page_dimensions.append((w, h))
    return page_dimensions

def get_color_counts(file_path):
    all_cmyk = {}
    all_rgb = {}
    doc = fitz.open(file_path)
    for page in doc:
        pix = page.get_pixmap()
        colors_rgb = pix.color_count(colors = True)
        colors_cmyk = {
            rgb_to_cmyk(x): colors_rgb[x] for x in colors_rgb
        }
        for cmyk, cnt in colors_cmyk.items():
            if cmyk not in all_cmyk:
                all_cmyk[cmyk] = 0
            all_cmyk[cmyk] += cnt
        for rgb, cnt in colors_rgb.items():
            if rgb not in all_rgb:
                all_rgb[rgb] = 0
            all_rgb[rgb] += cnt
    return all_cmyk, all_rgb


class PDFUtil: 
    def __init__(self, file_path):
        self.file_path = file_path
        self.cmyk_counts, self.rgb_counts = get_color_counts(file_path)
        self.page_dimensions = get_page_dimensions(file_path)
        self.npages = len(self.page_dimensions)
