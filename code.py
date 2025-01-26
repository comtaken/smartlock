import time
import digitalio
import board
import socketpool
import adafruit_httpserver as httpserver
import wifi
import adafruit_ntp
import rtc
import busio
import pwmio
from adafruit_motor import servo
# 書き込み禁止時、以下を実行し初期化
# import storage
# storage.erase_filesystem()

# 接続情報
SSID =
PASSWORD =

# 本体LEDの設定
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# サーボモータの設定 (GPIOピンは適宜変更)
pwm = pwmio.PWMOut(board.GP16, duty_cycle=0, frequency=50)
my_servo = servo.Servo(pwm)
lockFlg = ""

# サーボモータを元の位置（0度）に戻す
my_servo.angle = 0

# Wi-Fi接続を設定
try:
    wifi.radio.connect(SSID, PASSWORD)
    led.value = True
    ip_address = wifi.radio.ipv4_address
    print(f"Connected to Wi-Fi. IP Address: {ip_address}")
except Exception as e:
    print("NotConnected to Wi-Fi", e)

# ソケットプールとNTPクライアントの設定
pool = socketpool.SocketPool(wifi.radio)
rtc_clock = rtc.RTC()
ntp = adafruit_ntp.NTP(pool)

# NTPサーバーから時刻を取得してRTCに設定
try:
    rtc_clock.datetime = ntp.datetime
    print("NTP time synchronized")
except Exception as e:
    print("NTP synchronization failed:", e)

# オフセット（UTC+9時間）
JST_OFFSET = 9 * 3600

current_time = time.localtime(time.mktime(rtc_clock.datetime) + JST_OFFSET)
formatted_time = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
    current_time.tm_year,
    current_time.tm_mon,
    current_time.tm_mday,
    current_time.tm_hour,
    current_time.tm_min,
    current_time.tm_sec
)
# ログ
try:
    with open("pj.log", "a") as file:
        file.write(f"{formatted_time}　起動初期化　[code.py]\n")
    print("Successfully appended to pj.log")
except Exception as e:
    print(f"Error writing to pj.log: {e}")

server = httpserver.Server(pool)

@server.route("/")
def index(request):
    html = """
    <html>
    <meta charset="UTF-8">
    <head><title>Simple Web Page</title></head>
    <body>
    <h1 style="color:red">SMARTLOCK PJ</h1>
    <p>//TODO:html別出し</p>
    <p>Your IP address is: {}</p>
    <form action="/close">
        <button type="submit">Move Servo 120 Degrees</button>
    </form>
    <form action="/open">
        <button type="submit">Move Servo 0 Degrees</button>
    </form>
    </body>
    </html>
    """.format(wifi.radio.ipv4_address)
    return httpserver.Response(request, html, content_type="text/html")

@server.route("/close")
def move_servo(request):
    global lockFlg
    if(lockFlg == ""):
        my_servo.angle = 120
        lockFlg = "1"
    print(lockFlg)
    html = """
    <html>
    <meta charset="UTF-8">
    <head><title>Simple Web Page</title></head>
    <body>
    <h1 style="color:red">SMARTLOCK PJ</h1>
    <p>//TODO:html別出し</p>
    <p>Your IP address is: {}</p>
    <form action="/close">
        <button type="submit">Move Servo 120 Degrees</button>
    </form>
    <form action="/open">
        <button type="submit">Move Servo 0 Degrees</button>
    </form>
    </body>
    </html>
    """
    return httpserver.Response(request, html, content_type="text/html")

@server.route("/open")
def move_servo(request):
    global lockFlg
    if(lockFlg == "1"):
        my_servo.angle = 0
        lockFlg = ""
    print(lockFlg)
    html = """
    <html>
    <meta charset="UTF-8">
    <head><title>Simple Web Page</title></head>
    <body>
    <h1 style="color:red">SMARTLOCK PJ</h1>
    <p>//TODO:html別出し</p>
    <p>Your IP address is: {}</p>
    <form action="/close">
        <button type="submit">Move Servo 120 Degrees</button>
    </form>
    <form action="/open">
        <button type="submit">Move Servo 0 Degrees</button>
    </form>
    </body>
    </html>
    """
    return httpserver.Response(request, html, content_type="text/html")

server.start(port=8080)

while True:
    try:
        server.poll() 
    except Exception as e:
        print(f"Server error: {e}")
    time.sleep(1)
