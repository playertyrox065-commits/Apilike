import json
import time
import os
import threading
import asyncio
import random
import binascii
import gzip
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

import warnings
import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

from flask import Flask, jsonify, request
import requests
import aiohttp

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad as aes_pad
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import builder as _builder

_pool = _descriptor_pool.Default()

_uid_desc = _pool.AddSerializedFile(
    b'\n\x13uid_generator.proto\"0\n\ruid_generator\x12\x0f\n\x07saturn_\x18\x01 \x01(\x03\x12\x0e\n\x06garena\x18\x02 \x01(\x03\x62\x06proto3'
)
_uid_globals = {}
_builder.BuildMessageAndEnumDescriptors(_uid_desc, _uid_globals)
_builder.BuildTopDescriptorsAndMessages(_uid_desc, "uid_generator_pb2", _uid_globals)
UidGenerator = _uid_globals["uid_generator"]

_like_desc = _pool.AddSerializedFile(
    b'\n\nlike.proto\"#\n\x04like\x12\x0b\n\x03uid\x18\x01 \x01(\x03\x12\x0e\n\x06region\x18\x02 \x01(\tb\x06proto3'
)
_like_globals = {}
_builder.BuildMessageAndEnumDescriptors(_like_desc, _like_globals)
_builder.BuildTopDescriptorsAndMessages(_like_desc, "like_pb2", _like_globals)
LikeMsg = _like_globals["like"]

_lc_fdp = _descriptor_pb2.FileDescriptorProto()
_lc_fdp.name = "like_count.proto"
_lc_fdp.syntax = "proto3"

_lc_basic = _lc_fdp.message_type.add()
_lc_basic.name = "BasicInfo"
_lc_f1 = _lc_basic.field.add()
_lc_f1.name = "UID"; _lc_f1.number = 1; _lc_f1.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT64; _lc_f1.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
_lc_f3 = _lc_basic.field.add()
_lc_f3.name = "PlayerNickname"; _lc_f3.number = 3; _lc_f3.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING; _lc_f3.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
_lc_f5 = _lc_basic.field.add()
_lc_f5.name = "region"; _lc_f5.number = 5; _lc_f5.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING; _lc_f5.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
_lc_f6 = _lc_basic.field.add()
_lc_f6.name = "level"; _lc_f6.number = 6; _lc_f6.type = _descriptor_pb2.FieldDescriptorProto.TYPE_UINT32; _lc_f6.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL

_lc_f21 = _lc_basic.field.add()
_lc_f21.name = "Likes"; _lc_f21.number = 21; _lc_f21.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT64; _lc_f21.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL

_lc_info = _lc_fdp.message_type.add()
_lc_info.name = "Info"
_lc_a1 = _lc_info.field.add()
_lc_a1.name = "AccountInfo"; _lc_a1.number = 1; _lc_a1.type = _descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE; _lc_a1.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL; _lc_a1.type_name = ".BasicInfo"

_lc_desc = _pool.AddSerializedFile(_lc_fdp.SerializeToString())
_lc_globals = {}
_builder.BuildMessageAndEnumDescriptors(_lc_desc, _lc_globals)
_builder.BuildTopDescriptorsAndMessages(_lc_desc, "like_count_pb2", _lc_globals)
BasicInfo = _lc_globals["BasicInfo"]
Info = _lc_globals["Info"]

_login_desc = _pool.AddSerializedFile(
    b'\n\x0e\x46reeFire.proto"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t"]\n\x10\x42lacklistInfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\r"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME_AUTO_NEW\x10\xf6\x07\x62\x06proto3'
)
_login_globals = {}
_builder.BuildMessageAndEnumDescriptors(_login_desc, _login_globals)
_builder.BuildTopDescriptorsAndMessages(_login_desc, "FreeFire_pb2", _login_globals)
LoginReq = _login_globals["LoginReq"]
LoginRes = _login_globals["LoginRes"]

ACC_FILE = "account.json"
TOKEN_FILE = "token.json"
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
TOKEN_REFRESH_INTERVAL = 2 * 60 * 60  
LOGIN_RETRY = 2
REGION = "VN"
BP_BASE = "https://clientbp.ggpolarbear.com"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/MajorLogin"
RELEASE_VERSION = "OB55"
USER_AGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
UNITY_VERSION = "2018.4.12f1"
PLAY_VERSION = "1.132.1"
GA_SV = "1789534056"

_executor = ThreadPoolExecutor(max_workers=100)
TOKEN_POOL: dict = {}
LOGIN_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Encoding": "deflate, gzip",
    "X-Ga-Sv": GA_SV,
    "Authorization": "Bearer",
    "X-Ga": "v1 1",
    "Releaseversion": RELEASE_VERSION,
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Unity-Version": UNITY_VERSION,
    "PlAy_VeR": PLAY_VERSION,
    "Ob_VeR": RELEASE_VERSION,
}

app = Flask(__name__)

def aes_encrypt_raw(plaintext: bytes) -> bytes:
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(aes_pad(plaintext, AES.block_size))

def encrypt_message(plaintext: bytes) -> str:
    return binascii.hexlify(aes_encrypt_raw(plaintext)).decode()

def enc(uid: str) -> str:
    msg = UidGenerator()
    msg.saturn_ = int(uid)
    msg.garena = 1
    return encrypt_message(msg.SerializeToString())

async def _request_with_retry(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    **kwargs,
):
    for attempt in range(max_retries):
        try:
            async with session.request(method, url, **kwargs) as resp:
                if resp.status in (429, 502, 503, 504) and attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    delay += random.uniform(0, delay * 0.1)
                    await asyncio.sleep(delay)
                    continue
                if resp.status >= 400:
                    return None
                payload = await resp.read()
                enc_header = resp.headers.get("Content-Encoding", "")
                if "gzip" in enc_header:
                    try:
                        payload = gzip.decompress(payload)
                    except Exception:
                        pass
                return payload
        except asyncio.TimeoutError:
            if attempt >= max_retries - 1:
                return None
            await asyncio.sleep(base_delay)
        except Exception:
            if attempt >= max_retries - 1:
                return None
            await asyncio.sleep(base_delay)
    return None

async def get_oauth_token(
    session: aiohttp.ClientSession, uid: str, password: str
) -> Optional[dict]:
    payload = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    content = await _request_with_retry(
        session,
        "POST",
        "https://100067.connect.garena.com/oauth/guest/token/grant",
        data=payload,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    )
    if not content:
        return None
    try:
        data = json.loads(content)
    except Exception:
        return None
    access_token = data.get("access_token") or data.get("token") or data.get("session_key")
    open_id = data.get("open_id") or data.get("openid")
    if access_token and open_id:
        return {"access_token": access_token, "open_id": open_id}
    return None

def try_parse_login_res(data: bytes) -> Optional[dict]:
    try:
        msg = LoginRes()
        msg.ParseFromString(data)
        if msg.token:
            return {
                "account_id": str(msg.account_id),
                "token": msg.token,
                "lock_region": msg.lock_region,
            }
    except Exception:
        pass
    return None

def extract_login_res(raw: bytes) -> Optional[dict]:
    parsed = try_parse_login_res(raw)
    if parsed:
        return parsed
    idx = 0
    while True:
        idx = raw.find(b"\x08", idx)
        if idx == -1:
            break
        parsed = try_parse_login_res(raw[idx:])
        if parsed:
            return parsed
        idx += 1
    jwt_marker = raw.find(b"eyJhbGciOiJIUzI1NiIs")
    if jwt_marker != -1:
        for i in range(jwt_marker - 1, max(jwt_marker - 300, -1), -1):
            if raw[i] == 0x42:
                parsed = try_parse_login_res(raw[i:])
                if parsed:
                    return parsed
                break
    return None

async def major_login(
    session: aiohttp.ClientSession, access_token: str, open_id: str
) -> Optional[dict]:
    for platform_type in [4, 2, 3, 6, 8]:
        req = LoginReq()
        req.open_id = open_id
        req.open_id_type = "4"
        req.login_token = access_token
        req.orign_platform_type = str(platform_type)

        body = aes_encrypt_raw(req.SerializeToString())
        content = await _request_with_retry(
            session,
            "POST",
            LOGIN_URL,
            data=body,
            headers=LOGIN_HEADERS,
        )
        if not content:
            continue
        parsed = extract_login_res(content)
        if parsed and parsed.get("token"):
            return {
                "token": parsed["token"],
                "account_id": str(parsed.get("account_id", "")),
                "platform_type": platform_type,
            }
    return None

async def login_account_async(
    uid: str, password: str, session: aiohttp.ClientSession
) -> dict:
    for attempt in range(1, LOGIN_RETRY + 1):
        oauth = await get_oauth_token(session, uid, password)
        if not oauth:
            if attempt < LOGIN_RETRY:
                await asyncio.sleep(1 * attempt)
            continue
        result = await major_login(session, oauth["access_token"], oauth["open_id"])
        if not result or not result.get("token"):
            if attempt < LOGIN_RETRY:
                await asyncio.sleep(1 * attempt)
            continue
        return {"success": True, "uid": uid, "token": result["token"]}
    return {"success": False, "uid": uid, "error": "Login failed"}

def login_account(uid: str, password: str) -> dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        timeout = aiohttp.ClientTimeout(total=30)

        async def _run():
            async with aiohttp.ClientSession(timeout=timeout) as session:
                return await login_account_async(uid, password, session)

        return loop.run_until_complete(_run())
    finally:
        loop.close()

def load_accounts() -> list:
    if not os.path.exists(ACC_FILE):
        print(f"[Accounts] Không tìm thấy {ACC_FILE}")
        return []
    try:
        with open(ACC_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Accounts] Lỗi đọc {ACC_FILE}: {e}")
        return []

    if isinstance(data, dict):
        accounts = [{"uid": str(uid), "password": str(pw)} for uid, pw in data.items() if pw]
    elif isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            keys = list(first.keys())
            uid_pw_keys = [k for k in keys if k in ("uid", "password")]
            if len(uid_pw_keys) >= 2:
                accounts = [
                    {"uid": str(a["uid"]), "password": str(a["password"])}
                    for a in data if isinstance(a, dict) and "uid" in a and "password" in a
                ]
            else:
                combined = {}
                for item in data:
                    if isinstance(item, dict):
                        combined.update(item)
                accounts = [{"uid": str(k), "password": str(v)} for k, v in combined.items()]
        else:
            print(f"[Accounts] Định dạng {ACC_FILE} không hợp lệ")
            return []
    else:
        print(f"[Accounts] Định dạng {ACC_FILE} không hợp lệ: {type(data)}")
        return []

    if not accounts:
        print(f"[Accounts] Không tìm thấy account nào trong {ACC_FILE}")
        return []

    print(f"[Accounts] Loaded {len(accounts)} accounts từ {ACC_FILE}")
    return accounts

def _save_token_file(token_list: list):
    payload = {"created_at": time.time(), "tokens": token_list}
    tmp = TOKEN_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, TOKEN_FILE)

def _load_token_file() -> tuple:
    if not os.path.exists(TOKEN_FILE):
        return 0.0, []
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return 0.0, [t for t in data if t.get("token")]
        created_at = data.get("created_at", 0.0)
        tokens = [t for t in data.get("tokens", []) if t.get("token")]
        return created_at, tokens
    except Exception as e:
        print(f"[Token] Lỗi đọc {TOKEN_FILE}: {e}")
        return 0.0, []

def is_token_expired() -> bool:
    created_at, tokens = _load_token_file()
    if not tokens:
        return True
    return (time.time() - created_at) >= TOKEN_REFRESH_INTERVAL

def refresh_all_tokens():
    accounts = load_accounts()
    if not accounts:
        print("[Token] Không có account để refresh token.")
        return

    total = len(accounts)
    print(f"[Token] Lấy JWT cho {total} accounts...")
    token_list = []
    success_count = failed_count = 0
    PER_ACCOUNT_TIMEOUT = 30

    futures = {_executor.submit(login_account, a["uid"], a["password"]): a for a in accounts}
    pending = set(futures.keys())
    i = 0
    deadline = time.time() + total * PER_ACCOUNT_TIMEOUT

    while pending:
        remaining_time = deadline - time.time()
        if remaining_time <= 0:
            for f in pending:
                failed_count += 1
                print(f"[Token] ⏱️ {futures[f]['uid']}: Timeout — bỏ qua")
            break

        done, pending = wait(
            pending,
            timeout=min(PER_ACCOUNT_TIMEOUT, remaining_time),
            return_when=FIRST_COMPLETED,
        )
        if not done:
            for f in pending:
                failed_count += 1
                print(f"[Token] ⏱️ {futures[f]['uid']}: Bị treo — bỏ qua")
            break

        for future in done:
            i += 1
            acc = futures[future]
            try:
                result = future.result(timeout=1)
                if i % 10 == 0 or i == total:
                    print(f"[Token] ⏳ {i}/{total}")
                if result.get("success"):
                    token_list.append({"uid": result["uid"], "token": result["token"]})
                    success_count += 1
                    print(f"[Token] ✅ [{i}] {result['uid']}")
                else:
                    failed_count += 1
                    print(f"[Token] ❌ [{i}] {acc['uid']}: {result.get('error', 'Unknown')}")
            except Exception as e:
                failed_count += 1
                print(f"[Token] ❌ [{i}] {acc['uid']}: {e}")

    rate = success_count / total * 100 if total else 0
    print(f"[Token] ✅ {success_count} | ❌ {failed_count} | {rate:.1f}%")

    if token_list:
        _save_token_file(token_list)
        TOKEN_POOL[REGION] = {
            "all_tokens": [t["token"] for t in token_list],
            "current_index": 0,
            "total_tokens": len(token_list),
        }
        print(f"[Token] Đã lưu {len(token_list)} tokens → {TOKEN_FILE}")
    print("[Token] Refresh hoàn tất!")

def ensure_tokens_valid():
    if is_token_expired():
        print("[Token] Hết hạn hoặc chưa có → refresh...")
        refresh_all_tokens()
    else:
        _, token_list = _load_token_file()
        if token_list:
            TOKEN_POOL[REGION] = {
                "all_tokens": [t["token"] for t in token_list],
                "current_index": 0,
                "total_tokens": len(token_list),
            }
        created_at, _ = _load_token_file()
        remaining = TOKEN_REFRESH_INTERVAL - (time.time() - created_at)
        print(f"[Token] Còn hạn (~{int(remaining // 60)} phút), {len(token_list)} tokens.")

def token_refresh_loop():
    while True:
        try:
            if is_token_expired():
                print("[Token][Background] Hết hạn → refresh...")
                refresh_all_tokens()
        except Exception as e:
            print(f"[Token][Background] Lỗi: {e}")
        time.sleep(60)

def load_tokens() -> list:
    pool = TOKEN_POOL.get(REGION, {})
    if pool.get("all_tokens"):
        return [{"token": t} for t in pool["all_tokens"]]
    _, token_list = _load_token_file()
    return token_list

def get_next_token() -> str:
    if REGION not in TOKEN_POOL or TOKEN_POOL[REGION].get("total_tokens", 0) == 0:
        ensure_tokens_valid()
    pool = TOKEN_POOL.get(REGION, {})
    total = pool.get("total_tokens", 0)
    if total == 0:
        return ""
    idx = pool["current_index"]
    token = pool["all_tokens"][idx]
    pool["current_index"] = (idx + 1) % total
    return token

async def send_request(
    session: aiohttp.ClientSession, edata: bytes, token: str, url: str, headers: dict
):
    try:
        async with session.post(
            url, data=edata, headers={**headers, "Authorization": f"Bearer {token}"}
        ) as r:
            return await r.text()
    except Exception:
        return None

async def send_multiple_likes(uid: str, url: str) -> list:
    msg = LikeMsg()
    msg.uid = int(uid)
    msg.region = REGION
    encrypted = encrypt_message(msg.SerializeToString())
    edata = bytes.fromhex(encrypted)

    tokens = load_tokens()
    if not tokens:
        return []

    headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Unity-Version": UNITY_VERSION,
        "X-GA": "v1 1",
        "X-Ga-Sv": GA_SV,
        "ReleaseVersion": RELEASE_VERSION,
        "Releaseversion": RELEASE_VERSION,
        "Ob_VeR": RELEASE_VERSION,
        "PlAy_VeR": PLAY_VERSION,
    }
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, edata, t["token"], url, headers) for t in tokens]
        return await asyncio.gather(*tasks, return_exceptions=True)

def get_player_info(encrypted_uid_hex: str, token: str) -> Optional[dict]:
    url = BP_BASE + "/GetPlayerPersonalShow"
    headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Unity-Version": UNITY_VERSION,
        "X-GA": "v1 1",
        "X-Ga-Sv": GA_SV,
        "ReleaseVersion": RELEASE_VERSION,
        "Releaseversion": RELEASE_VERSION,
        "Ob_VeR": RELEASE_VERSION,
        "PlAy_VeR": PLAY_VERSION,
    }
    try:
        r = requests.post(
            url,
            data=bytes.fromhex(encrypted_uid_hex),
            headers=headers,
            verify=False,
            timeout=10,
        )
        if r.status_code != 200:
            return None
        info = Info()
        info.ParseFromString(r.content)
        if not info.AccountInfo:
            return None
        return {
            "UID": info.AccountInfo.UID,
            "PlayerNickname": info.AccountInfo.PlayerNickname,
            "Likes": info.AccountInfo.Likes,
            "Region": info.AccountInfo.region,
            "PlayerLevel": info.AccountInfo.level,
        }
    except Exception as e:
        print(f"[PlayerInfo] Error: {e}")
        return None

@app.route("/")
def index():
    return jsonify({"status": "Server đang chạy"}), 200

@app.route("/like", methods=["GET"])
def handle_like():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "UID is required"}), 400
    try:
        token = get_next_token()
        if not token:
            return jsonify({"error": "Không có token khả dụng"}), 500

        encrypted_uid = enc(uid)

        before = get_player_info(encrypted_uid, token)
        if not before:
            return jsonify({"error": "Không thể lấy thông tin player"}), 500
        before_like = int(before.get("Likes", 0))

        url = BP_BASE + "/LikeProfile"
        asyncio.run(send_multiple_likes(uid, url))

        after = get_player_info(encrypted_uid, token)
        if not after:
            return jsonify({"error": "Không thể lấy thông tin sau khi like"}), 500
        after_like = int(after.get("Likes", 0))
        like_given = after_like - before_like

        return jsonify({
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": after.get("PlayerNickname", ""),
            "PlayerRegion": after.get("Region", ""),
            "PlayerLevel": after.get("PlayerLevel", 0),
            "UID": after.get("UID", 0),
            "status": "success" if like_given > 0 else "failed",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/token-status", methods=["GET"])
def route_token_status():
    created_at, token_list = _load_token_file()
    elapsed = time.time() - created_at if created_at else 0
    remaining = max(0, TOKEN_REFRESH_INTERVAL - elapsed)
    return jsonify({
        "total_tokens": len(token_list),
        "expired": elapsed >= TOKEN_REFRESH_INTERVAL,
        "remaining_minutes": int(remaining // 60),
        "current_index": TOKEN_POOL.get(REGION, {}).get("current_index", 0),
    })

@app.route("/refresh-tokens", methods=["POST"])
def route_refresh_tokens():
    threading.Thread(target=refresh_all_tokens, daemon=True).start()
    return jsonify({"status": "refresh_started"}), 200

if __name__ == "__main__":
    print("[App] Khởi động Free Fire Like API Server...")
    print(f"[App] Account file: {ACC_FILE}")
    print(f"[App] Token file: {TOKEN_FILE}")
    print(f"[App] Region: {REGION}")

    ensure_tokens_valid()

    threading.Thread(target=token_refresh_loop, daemon=True).start()

    PORT = 3031
    print(f"[App] Server listening on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
