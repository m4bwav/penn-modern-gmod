-- gm_penn_modern walk test, installed by tools/walk.sh only. Runs when data/pm_walk_go.txt exists:
-- puts the player at the foot of each stair or escalator, holds +forward for a few seconds and
-- logs where the walk ended to data/pm_walk/result.txt (PASS when the end height is reached).
if game.GetMap() ~= "gm_penn_modern" then return end
if not file.Exists("pm_walk_go.txt", "DATA") then return end
file.Delete("pm_walk_go.txt")
file.CreateDir("pm_walk")
local ROUTES = {  -- name, start, yaw, seconds, end height to reach [, x to reach on a level walk] (tools/build_vmf.py)
  { "stair_south", Vector(-1176, -798, 40), 0, 5, 250 },
  { "stair_north", Vector(-1176, 798, 40), 0, 5, 250 },
  -- Escalators move (session 13): ride_* stand still (idle = true) and must arrive; against_* walk
  -- against the lane's travel and must still get through. Up lane y = centre -33 when it climbs +x.
  { "ride_south_up", Vector(-300, -273, -328), 0, 10, -4, idle = true },
  { "ride_south_down", Vector(320, -207, 8), 180, 10, -356, idle = true },
  { "against_south_dn", Vector(-420, -207, -356), 0, 10, -4 },
  { "against_south_up", Vector(380, -273, 4), 180, 10, -356 },
  { "ride_north_up", Vector(300, 273, -328), 180, 10, -4, idle = true },
  { "ride_north_down", Vector(-320, 207, 8), 0, 10, -356, idle = true },
  { "against_north_dn", Vector(420, 207, -356), 180, 10, -4 },
  { "against_north_up", Vector(-380, 273, 4), 0, 10, -356 },
  { "to_lirr", Vector(700, 0, -356), 0, 10, -360, 2300 },
  { "ride_lirr_up", Vector(4430, -233, -328), 0, 10, -4, idle = true },
  { "ride_lirr_down", Vector(5060, -167, 8), 180, 10, -356, idle = true },
  { "against_lirr_dn", Vector(4360, -167, -356), 0, 10, -4 },
  { "against_lirr_up", Vector(5110, -233, 4), 180, 10, -356 },
  { "ride_walk_east", Vector(1010, -68, -350), 0, 12, -356, 1860, idle = true },
  { "ride_walk_west", Vector(1870, 68, -350), 180, 12, -356, 1020, idle = true },
  { "against_walk_e", Vector(1010, 68, -350), 0, 12, -356, 1860 },
  { "against_walk_w", Vector(1870, -68, -350), 180, 12, -356, 1020 },
  { "to_amtrak", Vector(3024, -300, -356), 270, 6, -244 },
  { "ride_amtrak_up", Vector(3730, -1593, -564), 0, 10, -244, idle = true },
  { "ride_amtrak_down", Vector(4360, -1527, -228), 180, 10, -596, idle = true },
  { "against_amtrak_dn", Vector(3600, -1527, -596), 0, 10, -244 },
  { "against_amtrak_up", Vector(4420, -1593, -236), 180, 10, -596 },
  { "to_njt", Vector(4700, -1440, -236), 0, 8, -240, 5400 },
  { "njt_stair_down", Vector(7120, -1700, -236), 180, 8, -596 },
  { "njt_stair_up", Vector(6460, -1700, -596), 0, 8, -244 },
}
local out, cur, ply = {}, nil, nil
hook.Add("StartCommand", "pm_walk", function(p, cmd)
  if cur and p == ply then
    cmd:ClearButtons(); cmd:SetSideMove(0)
    if cur.idle then cmd:SetForwardMove(0) else cmd:SetButtons(IN_FORWARD); cmd:SetForwardMove(200) end
    cmd:SetViewAngles(Angle(0, cur[3], 0))
  end
end)
local function run(i)
  cur = ROUTES[i]
  if not cur then
    file.Write("pm_walk/result.txt", table.concat(out, "\n") .. "\n")
    file.Write("pm_walk/done.txt", "done")
    return
  end
  ply:SetPos(cur[2]); ply:SetEyeAngles(Angle(0, cur[3], 0)); ply:SetVelocity(-ply:GetVelocity())
  timer.Simple(cur[4], function()
    local p, want = ply:GetPos(), cur[5]
    local ok = (want > cur[2].z) and p.z >= want or (want < cur[2].z) and p.z <= want
    if cur[6] then  -- level walk: reach x (going west when the yaw is 180)
      ok = (cur[3] == 180 and p.x <= cur[6] or cur[3] ~= 180 and p.x >= cur[6]) and math.abs(p.z - want) < 8
    end
    out[#out + 1] = string.format("%-18s %s  end (%.0f, %.0f, %.0f), wanted z %s %d", cur[1],
      ok and "PASS" or "FAIL", p.x, p.y, p.z, want > cur[2].z and ">=" or "<=", want)
    run(i + 1)
  end)
end
timer.Simple(10, function() ply = Entity(1); if IsValid(ply) then run(1) end end)
