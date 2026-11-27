-- Installed by tools/shots.sh for shot runs only: spawn the player with no weapons, so the
-- physgun glow never shows in the screenshots.
if game.GetMap() ~= "gm_penn_modern" then return end
hook.Add("PlayerLoadout", "pm_shots_noweapons", function() return true end)
