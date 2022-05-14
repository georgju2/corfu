import os

def classify(basedir, ds, subject):
    ds = os.path.join(basedir, ds)
    os.system("docker run -ti -v {}/models:/tmp/models -v {}/json/model_class.json:/tmp/model_class.json -v {}.json:/tmp/dataset.json -v {}/{}:/tmp/image.png imageclass-inference".format(ds, ds, ds, ds, subject))

    return "INFERRED OK"

if __name__ == "__main__":
    basedir = "/tmp/"
    ds = "dataset_imageclass"

    # FIXME: code below assumes circles comes in first - might be another class though

    subject = None
    sfiles = os.listdir(os.path.join(basedir, ds, "test", "circle"))
    for sfile in sfiles:
        if sfile.endswith(".png"):
            subject = os.path.join("test", "circle", sfile)
            break

    print("=> Run classification for", basedir, ds, subject, "...")

    classify(basedir, ds, subject)
