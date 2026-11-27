-- Server autorun for tools/nav.sh: generate the nav mesh once, then report and quit.
-- Active only while data/pm_nav_go.txt exists. nav_generate saves maps/<map>.nav and reloads the map;
-- on the reload navmesh.IsLoaded() is true, so the count goes to data/pm_nav/done.txt.
if not file.Exists("pm_nav_go.txt", "DATA") then return end

hook.Add("InitPostEntity", "pm_nav", function()
	timer.Simple(5, function()
		if navmesh.IsLoaded() and navmesh.GetNavAreaCount() > 0 then
			file.CreateDir("pm_nav")
			file.Write("pm_nav/done.txt", "areas " .. navmesh.GetNavAreaCount() .. "\n")
			timer.Simple(2, function() RunConsoleCommand("quit") end)
		else
			RunConsoleCommand("nav_quicksave", "1")
			RunConsoleCommand("nav_generate")
		end
	end)
end)
