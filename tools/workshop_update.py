"""Update a Garry's Mod Workshop item's description, visibility and preview images
through the Steamworks flat API in GMod's own steam_api64.dll (Steam must be running).

python tools/workshop_update.py ID [--desc FILE] [--public] [--preview IMG ...]
"""
import argparse, ctypes, os, sys, time

GMOD = os.environ.get("GMOD", r"D:\SteamLibrary\steamapps\common\GarrysMod")
ap = argparse.ArgumentParser()
ap.add_argument("id", type=int)
ap.add_argument("--desc")
ap.add_argument("--title")
ap.add_argument("--public", action="store_true")
ap.add_argument("--preview", nargs="*", default=[])
a = ap.parse_args()

os.environ["SteamAppId"] = "4000"
os.environ["SteamGameId"] = "4000"
dll = ctypes.CDLL(os.path.join(GMOD, "bin", "win64", "steam_api64.dll"))
err = ctypes.create_string_buffer(1024)
dll.SteamAPI_InitFlat.argtypes = [ctypes.c_char_p]
if dll.SteamAPI_InitFlat(err) != 0:
    sys.exit("SteamAPI init failed: " + err.value.decode(errors="replace"))
V = ctypes.c_void_p
dll.SteamAPI_SteamUGC_v021.restype = V
dll.SteamAPI_SteamUtils_v010.restype = V
ugc, utils = dll.SteamAPI_SteamUGC_v021(), dll.SteamAPI_SteamUtils_v010()
f = dll.SteamAPI_ISteamUGC_StartItemUpdate
f.argtypes, f.restype = [V, ctypes.c_uint32, ctypes.c_uint64], ctypes.c_uint64
h = f(ugc, 4000, a.id)
def call(name, *args, types):
    fn = getattr(dll, "SteamAPI_ISteamUGC_" + name)
    fn.argtypes, fn.restype = [V, ctypes.c_uint64] + types, ctypes.c_bool
    if not fn(ugc, h, *args):
        sys.exit(name + " refused")
if a.title:
    call("SetItemTitle", a.title.encode(), types=[ctypes.c_char_p])
if a.desc:
    call("SetItemDescription", open(a.desc, encoding="utf-8").read().encode("utf-8"), types=[ctypes.c_char_p])
if a.public:
    call("SetItemVisibility", 0, types=[ctypes.c_int])
for p in a.preview:
    call("AddItemPreviewFile", os.path.abspath(p).encode(), 0, types=[ctypes.c_char_p, ctypes.c_int])
s = dll.SteamAPI_ISteamUGC_SubmitItemUpdate
s.argtypes, s.restype = [V, ctypes.c_uint64, ctypes.c_char_p], ctypes.c_uint64
api = s(ugc, h, b"Description, credits and previews")
done = dll.SteamAPI_ISteamUtils_IsAPICallCompleted
done.argtypes, done.restype = [V, ctypes.c_uint64, ctypes.POINTER(ctypes.c_bool)], ctypes.c_bool
failed = ctypes.c_bool()
for _ in range(1200):
    dll.SteamAPI_RunCallbacks()
    if done(utils, api, ctypes.byref(failed)):
        break
    time.sleep(0.25)
else:
    sys.exit("timed out")
# SubmitItemUpdateResult_t: EResult m_eResult (int32), bool needs legal agreement, uint64 id
buf = (ctypes.c_uint8 * 24)()
r = dll.SteamAPI_ISteamUtils_GetAPICallResult
r.argtypes = [V, ctypes.c_uint64, V, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_bool)]
r.restype = ctypes.c_bool
r(utils, api, buf, 24, 3404, ctypes.byref(failed))
eres = int.from_bytes(bytes(buf[:4]), "little")
print("EResult", eres, "(1 = OK)", "legal agreement needed" if buf[4] else "")
dll.SteamAPI_Shutdown()
sys.exit(0 if eres == 1 else 1)
