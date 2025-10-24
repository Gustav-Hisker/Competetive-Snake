import os
import random
import subprocess
import sys
from os import makedirs
from random import randrange
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse

from subprocess import Popen, PIPE

from starlette.responses import StreamingResponse

pyPath = "./python-submissions/"
cppPath = "./cpp-submissions/"
exePath = "./executable-submissions/"

compileTimeout = 10

makedirs(pyPath, exist_ok=True)
makedirs(cppPath, exist_ok=True)
makedirs(exePath, exist_ok=True)

class ProgramHandler:
    def __init__(self, path: str, n: int, k: int):
        self.path = path
        self.n = n
        self.k = k

        if path.endswith(".py"):
            self.p = Popen([sys.executable, "-u", path], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
        else:
            self.p = Popen(path, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)

        # Send initial input
        self.p.stdin.write(f"{n} {k}\n")
        self.p.stdin.flush()


    def sendGraph(self, g: list[set[int]]) -> None:
        for line in g:
            line = sorted(line)
            self.p.stdin.write(" ".join(map(str, line)) + "\n")
            self.p.stdin.flush()


    def getOutput(self) -> set[int]:
        result = self.p.stdout.readline()
        if not result:
            raise Exception("No output received from subprocess")
        result_set = set(map(int, result.strip().split()))
        result_set.intersection_update(range(self.n))
        result_set.difference_update({self.k})
        return result_set


    def __del__(self):
        try:
            self.p.kill()
        except Exception:
            pass


def testProgram(path: str):
    for i in range(100):
        try:
            n = random.randint(2,20)
            k = random.randrange(n)
            nWithoutK = list(set(range(n)).difference({k}))

            p = ProgramHandler(path, n, k)
            for _ in range(100):
                cols = p.getOutput()
                p.sendGraph([(set(random.sample(nWithoutK, randrange(n-1))) if j != k else cols) for j in range(n)])
            del p
        except Exception as e:
            yield False, e
            return
        yield True, i+1


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html") as f:
        return f.read()

@app.get("/example.png")
def load_example_image():
    def iterfile():
        with open("./example.png", mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="png")

# PYTHON
@app.post("/upload.py", response_class=HTMLResponse)
def wrapperUploadPy(team: Annotated[str, Form()], file: UploadFile = File(...)):
    return StreamingResponse(uploadPy(team, file), media_type="html")

def uploadPy(team: Annotated[str, Form()], file: UploadFile = File(...)):
    with open("preset.html") as f:
        yield f.read()
    yield "<h2>Submitting python file</h2>"
    yield "<h4>Uploading ...</h4>"
    try:
        with open(pyPath + team + ".py", "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        file.file.close()
        yield f"There was an error uploading the file:\n {e}"
        yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
        return
    finally:
        file.file.close()

    yield "<p>Upload successful</p>"
    yield "<h4>Testing upload</h4>"
    yield '<progress id="pb" max="100" value="0"></progress>'
    yield "<script>pb = document.getElementById('pb')</script>"

    for tr in testProgram(pyPath + team + ".py"):
        testSuccess, value = tr
        if testSuccess:
            yield f"<script>pb.value={value}</script>"
        else:
            yield f"<p>Error your programm didn't pass the tests. But created this Error.<br>{value}</p><p>Note that these tests shouldn't be a challenge but just find potential flaws in your code. Your code is tested in $100$ random games with $100$ rounds (every input your program gets, is an input that actually could occur in the game).</p>"
            yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
            return

    yield "<p>All tests successful.<p>"

    yield "<h3>Done!<h3>"
    yield "<p>You can now return to start page.</p>"
    yield "<a href='/'><button>Return</button></a>"

    yield "</body></html>"
    return

# C++
@app.post("/upload.cpp", response_class=HTMLResponse)
def wrapperUploadCpp(team: Annotated[str, Form()], file: UploadFile = File(...)):
    return StreamingResponse(uploadCpp(team, file), media_type="html")

def uploadCpp(team: Annotated[str, Form()], file: UploadFile = File(...)):
    with open("preset.html") as f:
        yield f.read()
    yield "<h2>Submitting C++ file</h2>"
    yield "<h4>Uploading ...</h4>"
    try:
        with open(cppPath + team + ".cpp", "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        file.file.close()
        yield f"<p>There was an error uploading the file:</p><br><code>{e}</code>"
        yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
        return
    finally:
        file.file.close()

    yield "<p>Upload successful</p>"
    yield "<h4>Compiling</h4>"
    yield "<p>Compilation successful</p>"
    es = ""
    try:
        subp = subprocess.run(f"g++ -std=c++20 -o {exePath}{team} {cppPath}{team}.cpp",shell=True, capture_output=True, timeout=compileTimeout)
        es = subp.stderr.decode()
        subp.check_returncode()
    except Exception as e:
        yield f"<p>There was an error compiling the your code:</p><code style='color: red'>{e}</code><br><br><p>stderr:</p><code style='color: red'>{es}</code>"
        yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
        return
    yield "<h4>Testing upload</h4>"
    yield '<progress id="pb" max="100" value="0"></progress>'
    yield "<script>pb = document.getElementById('pb')</script>"

    for tr in testProgram(exePath + team):
        testSuccess, value = tr
        if testSuccess:
            yield f"<script>pb.value={value}</script>"
        else:
            yield f"<p>Error your programm didn't pass the tests. But created this Error.<br>{value}</p><a href='/'><button>Return to start page</button></a></body></html>"
            return

    yield "<p>All tests successful.<p>"

    yield "<h3>Done!<h3>"
    yield "<p>You can now return to start page.</p>"
    yield "<a href='/'><button>Return</button></a>"

    yield "</body></html>"
    return

# EXECUTABLE
@app.post("/upload.exe", response_class=HTMLResponse)
def wrapperUploadExe(team: Annotated[str, Form()], file: UploadFile = File(...)):
    return StreamingResponse(uploadExe(team, file), media_type="html")

def uploadExe(team: Annotated[str, Form()], file: UploadFile = File(...)):
    with open("preset.html") as f:
        yield f.read()
    yield "<h2>Submitting executable</h2>"
    yield "<h4>Uploading ...</h4>"
    try:
        with open(exePath + team, "wb") as f:
            f.write(file.file.read())
        subprocess.run(f"chmod +x {exePath}{team}", shell=True, capture_output=True, timeout=compileTimeout, check=True)
    except Exception as e:
        file.file.close()
        yield f"<p>There was an error uploading the file:</p><br><code>{e}</code>"
        yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
        return
    finally:
        file.file.close()

    yield "<p>Upload successful</p>"
    yield "<h4>Testing upload</h4>"
    yield '<progress id="pb" max="100" value="0"></progress>'
    yield "<script>pb = document.getElementById('pb')</script>"

    for tr in testProgram(exePath + team):
        testSuccess, value = tr
        if testSuccess:
            yield f"<script>pb.value={value}</script>"
        else:
            yield f"<p>Error your programm didn't pass the tests. But created this Error.<br>{value}</p>"
            yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
            return

    yield "<p>All tests successful.<p>"

    yield "<h3>Done!<h3>"
    yield "<p>You can now return to start page.</p>"
    yield "<a href='/'><button>Return</button></a>"

    yield "</body></html>"
    return



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)