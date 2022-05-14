import pylab
import scipy.ndimage
import time
import tempfile
import os

def processimage(imgpath):
    print("[imagetune] reading image:", imgpath, "...")
    img = pylab.imread(imgpath)
    print("[imagetune] read image, dimensions", img.shape)

    print("[imagetune] blur...")
    t_start = time.time()
    blurimg = scipy.ndimage.gaussian_filter(img, sigma=2)
    t_diff = time.time() - t_start
    print("[imagetune] blurred after", round(t_diff, 2), "s")

    print("[imagetune] rotate...")
    t_start = time.time()
    rotimg = scipy.ndimage.rotate(blurimg, angle=45)
    t_diff = time.time() - t_start
    print("[imagetune] rotated after", round(t_diff, 2), "s")

    print("[imagetune] image processed, dimensions", rotimg.shape)

    print("[imagetune] saving image...")

    out = tempfile.NamedTemporaryFile(prefix="imagetune_", suffix="."+imgpath.split(".")[-1], delete=False)

    pylab.imsave(out, rotimg)

    out.close()

    print("[imagetune] saved as:", out.name)

    return out.name

if __name__ == "__main__":
    fn = "foggy-path-landscape.jpg"
    print("[main] run image processing:", fn)
    procfn = processimage(fn)
    print("[main] image processing done:", procfn)
    os.unlink(procfn)
