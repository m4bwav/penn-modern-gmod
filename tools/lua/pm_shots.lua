-- gm_penn_modern screenshot rig. Runs only when data/pm_shots_go.txt exists
-- (tools/shots.sh writes it); captures each camera to data/pm_shots/, then quits.
if SERVER then return end
if not file.Exists("pm_shots_go.txt", "DATA") then return end
if game.GetMap() ~= "gm_penn_modern" then return end
-- The go file may list camera names (one line, spaces); "go" means all.
local want = string.Trim(file.Read("pm_shots_go.txt", "DATA") or "go")
file.Delete("pm_shots_go.txt")
file.CreateDir("pm_shots")

local CAMS = {  -- starter cameras for the placeholder Moynihan hall; sized to the 200 x 155 ft blockout
  { "hall_west", Vector(-1050, 0, 72), Angle(-8, 0, 0) },
  { "hall_up",   Vector(0, 0, 72), Angle(-70, 0, 0) },
  { "hall_east", Vector(1050, 0, 72), Angle(-8, 180, 0) },
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
