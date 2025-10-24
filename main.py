import random
import subprocess
import sys
from os import makedirs
from random import randrange
from types import TracebackType
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

appleSpawnPeriod = 20

makedirs(pyPath, exist_ok=True)
makedirs(cppPath, exist_ok=True)
makedirs(exePath, exist_ok=True)

class ProgramHandler:
    def __init__(self, path: str, w: int, h: int):
        self.path = path
        self.w = w
        self.h = h

        if path.endswith(".py"):
            self.p = Popen([sys.executable, "-u", path], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
        else:
            self.p = Popen(path, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)

        # Send initial input
        self.p.stdin.write(f"{w} {h}\n")
        self.p.stdin.flush()


    def sendBoard(self, b: list[list[int]]) -> None:
        for line in b:
            self.p.stdin.write(" ".join(map(str, line)) + "\n")
            self.p.stdin.flush()


    def getOutput(self) -> str:
        result = self.p.stdout.readline()
        if result == "":
            # Check if the process died
            retcode = self.p.poll()
            if retcode is not None:
                err = self.p.stderr.read()
                raise Exception(f"Subprocess {self.path} exited with code {retcode}.\nStderr:\n{err}")
            else:
                raise Exception(f"No output received from subprocess {self.path}")
        return result.strip()


    def __del__(self):
        try:
            self.p.kill()
        except Exception:
            pass


def dToV(d):
    return {"d":(0,1),"u":(0,-1),"l":(-1,0),"r":(1,0)}[d]

def dVSum(d,v):
    u = dToV(d)
    return u[0]+v[0],u[1]+v[1]


class Board:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.b = [[0 for _ in range(w)] for _ in range(h)]
        self.b[0][0] = 1
        self.b[-1][-1] = 2
        self.spawnApple()
        self.nextApple = appleSpawnPeriod

    # returns whether the game ended by this
    def spawnApple(self)->bool:
        free_fields = 0
        for i in range(0, self.w):
            for j in range(0, self.h):
                free_fields += 1 if self.b[j][i] == 0 else 0

        if free_fields == 0:
            return True

        a = randrange(0, free_fields)

        for i in range(0, self.w):
            for j in range(0, self.h):
                if self.b[j][i] == 0:
                    if a == 0:
                        self.b[j][i] = -1
                    a -= 1

        return False

    def getP1Board(self) -> list[list[int]]:
        return self.b

    def getP2Board(self) -> list[list[int]]:
        return [[self.b[-j-1][-i-1] for i in range(self.w)] for j in range(self.h)]

    def turn(self, o1:str, o2:str):
        head1cords = ()
        head2cords = ()
        end1 = 0
        end1cords = ()
        end2 = 0
        end2cords = ()
        for i in range(0, self.w):
            for j in range(0, self.h):
                if self.b[j][i] == -1:
                    continue
                if self.b[j][i] == 1:
                    head1cords = (i,j)
                elif self.b[j][i] == 2:
                    head2cords = (i,j)
                if self.b[j][i]%2 != 0:
                    if self.b[j][i] > end1:
                        end1 = self.b[j][i]
                        end1cords = (i,j)
                else:
                    if self.b[j][i] > end2:
                        end2 = self.b[j][i]
                        end2cords = (i,j)


        n1x, n1y = dVSum(o1, head1cords)
        n2x, n2y = dVSum(o2, head2cords)

        print("fuck it")
        e1x, e1y = end1cords
        e2x, e2y = end2cords


        wc1 = not (0 <= n1x < self.w and 0 <= n1y < self.h)
        wc2 = not (0 <= n2x < self.w and 0 <= n2y < self.h)

        print("das war absehbar")
        if not wc1:
            if self.b[n1y][n1x] != -1:
                self.b[e1y][e1x] = 0
        if not wc2:
            if self.b[n2y][n2x] != -1:
                self.b[e2y][e2x] = 0

        print("test123")

        c1 = wc1 or (self.b[n1y][n1x] != 0 and self.b[n1y][n1x] != -1)
        c2 = wc2 or (self.b[n2y][n2x] != 0 and self.b[n2y][n2x] != -1)

        if c1 and c2:
            return True, 0, "Simultaneous Crash"
        if c1:
            return True, 2, ("Wall Crash" if wc1 else "Snake Crash")
        if c2:
            return True, 1, ("Wall Crash" if wc2 else "Snake Crash")

        for i in range(0, self.w):
            for j in range(0, self.h):
                if self.b[j][i] != 0 and self.b[j][i] != -1:
                    self.b[j][i] += 2

        if n1x==n2x and n1y==n2y:
            return True, (1 if end1>end2 else (2 if end1<end2 else 0)) , "Headbutt"

        self.b[n1y][n1x] = 1
        self.b[n2y][n2x] = 2

        self.nextApple -= 1
        if self.nextApple <= 1:
            self.nextApple = appleSpawnPeriod
            end = self.spawnApple()
            if end:
                return True, (1 if end1>end2 else (2 if end1<end2 else 0)) , ("Apple Tie" if end1 == end2 else "Apple Tiebreak")



        return False, 0, ""


def convert2Input(d):
    return {"d":"u","u":"d","l":"r","r":"l"}[d]


def game(board: Board, p1: ProgramHandler, p2: ProgramHandler) -> (int, str):
    while True:
        p1.sendBoard(board.getP1Board())
        p2.sendBoard(board.getP2Board())

        o1 = p1.getOutput()
        if o1 not in {"d","u","l","r"}:
            return 2, "Surrender"
        o2 = p2.getOutput()
        if o2 not in {"d","u","l","r"}:
            return 1, "Surrender"

        print("test")
        end, win, reason = board.turn(o1, convert2Input(o2))
        print("das kommt unerwartet")

        if end:
            return win, reason


def testProgram(path: str):
    for i in range(100):
        try:
            w = random.randint(2,20)
            h = random.randint(2,20)

            p = ProgramHandler(path, w, h)
            o = ProgramHandler("./submission-examples/outer-edge.py", w, h)

            winner, reason = game(Board(w, h), o, p)

            warning = ""
            if winner == 2:
                warning = f"Your program lost against the example code. Reason: {reason}"

            del p, o

            yield True, i + 1, warning
        except Exception as e:
            yield False, e, ""
            return


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
        testSuccess, value, warning = tr
        if testSuccess:
            yield f"<script>pb.value={value}</script>"
        else:
            yield f"<p style='color:red'><b>Error<b> your programm didn't pass the tests. But created this Error:<br><code>{value}</code></p><p>Note that these tests shouldn't be a challenge but just find potential flaws in your code. Your code is tested in $100$ random games with $100$ rounds (every input your program gets, is an input that actually could occur in the game).</p>"
            yield "<br><a href='/'><button>Return to start page</button></a></body></html>"
            return
        if warning:
            yield f"<p style='color:yellow'><b>WARNING:</b> {warning}</p>"

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