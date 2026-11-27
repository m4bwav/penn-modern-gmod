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
  { "esc_south_up", Vector(-420, -240, -356), 0, 6, -4 },
  { "esc_north_up", Vector(420, 240, -356), 180, 6, -4 },
  { "esc_south_down", Vector(380, -240, 4), 180, 6, -356 },
  { "to_lirr", Vector(700, 0, -356), 0, 10, -360, 2300 },
  { "esc_lirr_up", Vector(4360, -200, -356), 0, 6, -4 },
  { "to_amtrak", Vector(3024, -300, -356), 270, 6, -244 },
  { "esc_amtrak_down", Vector(4420, -1560, -236), 180, 6, -596 },
  { "esc_amtrak_up", Vector(3600, -1560, -596), 0, 6, -244 },
  { "to_njt", Vector(4700, -1440, -236), 0, 8, -240, 5400 },
}
local out, cur, ply = {}, nil, nil
hook.Add("StartCommand", "pm_walk", function(p, cmd)
  if cur and p == ply then
    cmd:ClearButtons(); cmd:SetButtons(IN_FORWARD); cmd:SetForwardMove(200); cmd:SetSideMove(0)
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
    if cur[6] then ok = p.x >= cur[6] and math.abs(p.z - want) < 8 end  -- level walk: reach x
    out[#out + 1] = string.format("%-15s %s  end (%.0f, %.0f, %.0f), wanted z %s %d", cur[1],
      ok and "PASS" or "FAIL", p.x, p.y, p.z, want > cur[2].z and ">=" or "<=", want)
    run(i + 1)
  end)
end
timer.Simple(10, function() ply = Entity(1); if IsValid(ply) then run(1) end end)
