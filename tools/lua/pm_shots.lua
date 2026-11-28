-- gm_penn_modern screenshot rig. Runs only when data/pm_shots_go.txt exists
-- (tools/shots.sh writes it); captures each camera to data/pm_shots/, then quits.
if SERVER then return end
if not file.Exists("pm_shots_go.txt", "DATA") then return end
if game.GetMap() ~= "gm_penn_modern" then return end
-- The go file may list camera names (one line, spaces); "go" means all.
local want = string.Trim(file.Read("pm_shots_go.txt", "DATA") or "go")
file.Delete("pm_shots_go.txt")
file.CreateDir("pm_shots")

local CAMS = {  -- Moynihan blockout (session 2): 200 x 155 ft hall, wells, side halls, lower stub
  { "hall_west",  Vector(-1100, 0, 72), Angle(-14, 0, 0) },
  { "hall_up",    Vector(0, 0, 72), Angle(-70, 0, 0) },
  { "hall_east",  Vector(1100, 0, 72), Angle(-14, 180, 0) },
  { "wells",      Vector(-500, -560, 200), Angle(20, 30, 0) },
  { "side_south", Vector(-650, -700, 72), Angle(-5, 20, 0) },
  { "stair", Vector(-500, -720, 120), Angle(10, 190, 0) },
  { "lower",      Vector(-780, 0, -290), Angle(-5, 0, 0) },
  { "passage",    Vector(700, 0, -290), Angle(0, 0, 0) },
  { "walkway",    Vector(940, -160, -240), Angle(22, 25, 0) },
  { "esc_tread",  Vector(-100, -420, 120), Angle(40, 80, 0) },
  { "lirr_west",  Vector(2100, -250, -290), Angle(-3, 8, 0) },
  { "pavilion",   Vector(3700, 150, -290), Angle(-12, -10, 0) },
  { "lirr_east",  Vector(6780, 200, -290), Angle(-3, 185, 0) },
  { "mezz",       Vector(5350, 250, 72), Angle(10, 200, 0) },
  { "tvm",        Vector(2720, -60, -300), Angle(8, -90, 0) },
  { "amtrak_stair", Vector(3024, -250, -300), Angle(-12, -90, 0) },
  { "amtrak_north", Vector(3024, -760, -175), Angle(-4, -75, 0) },
  { "amtrak_west",  Vector(2150, -1560, -175), Angle(-6, 0, 0) },
  { "amtrak_board", Vector(3600, -1350, -180), Angle(-8, 90, 0) },
  { "amtrak_wait",  Vector(2660, -1960, -175), Angle(8, -140, 0) },
  { "njt_west",     Vector(5000, -1440, -175), Angle(-8, 0, 0) },
  { "njt_vault",    Vector(6000, -1440, -190), Angle(-35, 10, 0) },
  { "njt_gates",    Vector(5800, -1500, -180), Angle(0, 55, 0) },
  { "njt_tickets",  Vector(6100, -1250, -180), Angle(0, 215, 0) },
  { "plat_west",    Vector(2600, -1600, -530), Angle(4, 0, 0) },
  { "plat_train",   Vector(3300, -1450, -540), Angle(2, 20, 0) },
  { "plat_esc",     Vector(3200, -1560, -530), Angle(-10, 0, 0) },
  { "plat_stair",   Vector(6200, -1700, -530), Angle(-14, 0, 0) },
  { "njt_stairtop", Vector(7250, -1700, -175), Angle(30, 180, 0) },
  { "amtrak_esc",   Vector(4600, -1400, -170), Angle(22, 200, 0) },
}
if want ~= "go" then
  local keep, set = {}, {}
  for n in string.gmatch(want, "%S+") do set[n] = true end
  for _, c in ipairs(CAMS) do if set[c[1]] then keep[#keep + 1] = c end end
  CAMS = keep
end
local i, cam, frames = 0, nil, 0
-- The view moves by CalcView but the server sends entities by the player's PVS: move the player
-- to each camera (setpos needs sv_cheats, shots.sh sets it), else brush entities in rooms out of
-- sight of the spawn (tm_decor, hy_decor) are never networked and never drawn.
local function goto_cam()
  if cam then RunConsoleCommand("setpos", cam[2].x, cam[2].y, cam[2].z - 64) end
end
local ft, fpslog = 0, {}  -- frame time summed over frames 31-89, one fps line per camera

hook.Add("CalcView", "pm_shots", function()
  if cam then return { origin = cam[2], angles = cam[3], fov = 90, drawviewer = false } end
end)
hook.Add("HUDShouldDraw", "pm_shots", function() if cam then return false end end)
-- Hide the held weapon (the physgun glowed at the right edge of every shot).
hook.Add("PreDrawViewModel", "pm_shots", function() if cam then return true end end)
hook.Add("PostRender", "pm_shots", function()
  if not cam then return end
  frames = frames + 1
  if frames > 30 then ft = ft + RealFrameTime() end
  if frames < 90 then return end
  fpslog[#fpslog + 1] = string.format("%-14s %4.0f fps%s", cam[1], 59 / math.max(ft, 1e-4),
    bit.band(util.PointContents(cam[2]), CONTENTS_SOLID) ~= 0 and "  CAMERA IN SOLID" or "")
  ft = 0
  local data = render.Capture({ format = "jpg", quality = 92, x = 0, y = 0, w = ScrW(), h = ScrH() })
  file.Write("pm_shots/" .. cam[1] .. ".jpg", data)
  i, frames = i + 1, 0
  cam = CAMS[i]
  goto_cam()
  if not cam then
    file.Write("pm_shots/fps.txt", table.concat(fpslog, "\n") .. "\n")
    file.Write("pm_shots/done.txt", "done")
    timer.Simple(1, function() RunConsoleCommand("quit") end)
  end
end)
timer.Simple(8, function()
  RunConsoleCommand("mat_autoexposure_max", "1.5")
  i = 1; cam = CAMS[1]; goto_cam()
end)
